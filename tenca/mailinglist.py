from . import exceptions, pipelines, settings, templates

import base64
import hashlib
import urllib.parse
import urllib.error

import mailmanclient


class MailingList(object):

	"""A decorator for mailmanclient.restobjects.mailinglist.MailingList"""

	# Can be extended by settings.LIST_DEFAULT_SETTINGS
	# In case of conflicting entries, settings wins.
	SHARED_LIST_DEFAULT_SETTINGS = {
		'advertised': False,
		'default_member_action': 'accept',
		'default_nonmember_action': 'accept'
		# Disabled for mailman < 3.3.3
		# 'send_goodbye_message': False,
	}

	# Maps Mailman Template names to Tenca Template Names
	TEMPLATE_MAPPINGS = {
		'list:member:regular:footer': 'mail_footer',
		'list:user:action:subscribe': 'subscription_message',
		'list:user:action:unsubscribe': 'unsubscription_message',
		'list:user:notice:welcome': 'creation_message',
		'list:user:notice:rejected': 'rejected_message',
	}

	def __init__(self, connection, list):
		self.conn = connection
		self.list = list
		self.template_args = dict(
			fqdn_listname=self.fqdn_listname,
			action_link=pipelines.call_func(settings.BUILD_ACTION_LINK, self, '$token'),
			action_abuse_link=pipelines.call_func(settings.BUILD_ACTION_ABUSE_LINK, self, '$token'),
			invite_link=pipelines.call_func(settings.BUILD_INVITE_LINK, self),
			web_ui='{}://{}'.format(settings.WEB_UI_SCHEME, settings.WEB_UI_HOSTNAME)
		)

	def __repr__(self):
		return "<{} '{}'>".format(type(self).__name__, str(self.fqdn_listname))

	def _raise_nomember(self, email):
		raise exceptions.NoMemberException('{} is not a member address of {}'.format(email, self.fqdn_listname))

	def add_member_silently(self, email):
		"""Subscribe an email address to a mailing list, with no verification or notification send"""
		self.list.subscribe(email, pre_verified=True, pre_confirmed=True, send_welcome_message=False)

	def add_member(self, email, send_welcome_message=False):
		"""Subscribes a user and sends them a confirmation mail

		Returns the authentication token for that subscription.
		"""
		return self.list.subscribe(email, send_welcome_message=send_welcome_message)["token"]

	def configure_list(self):
		self.list.settings.update(self.SHARED_LIST_DEFAULT_SETTINGS)
		self.list.settings.update(settings.LIST_DEFAULT_SETTINGS)
		self.list.settings['subject_prefix'] = '[{}] '.format(self.list.settings['list_name'].lower())
		if settings.DEFAULT_OWNER_ADDRESS is not None:
			self.list.settings['owner_address'] = settings.DEFAULT_OWNER_ADDRESS
		self.list.settings['description'] = self.hashid
		for mailman_template_name, tenca_template_name in self.TEMPLATE_MAPPINGS.items():
			self.list.set_template(mailman_template_name, templates.http_substitute_url(
				tenca_template_name, **self.template_args
			))
		self.list.settings.save()

	def pending_subscriptions(self, request_type='subscription'):
		"""As of mailman<3.3.3 no unsubscriptions are delivered via REST.
		In case you updated core (but use an older version of mailmanclient),
		the following might do:

		path = 'lists/{}/requests'.format(self.fqdn_listname)
		get_params = {
			'token_owner': 'subscriber',
			'request_type': request_type
		}
		response, answer = self.conn.rest_call('{}?{}'.format(path, urllib.parse.urlencode(get_params), None, 'GET'))
		if 'entries' not in answer:
			return {}
		else:
			return {r['token']: r['email'] for r in answer['entries']}
		"""
		return {r['token']: r['email'] for r in self.list.get_requests(token_owner='subscriber')}

	def _wrap_subscription_exception(self, func, token):
		try:
			func()
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e, exceptions.NoSuchRequestException, self, token)

	def confirm_subscription(self, token):
		self._wrap_subscription_exception(
			lambda: self.list.accept_request(token),
			token)

	def cancel_pending_subscription(self, token):
		self._wrap_subscription_exception(
			lambda: self.list.moderate_request(token, 'discard'),
			token)

	def promote_to_owner(self, email):
		try:
			member = self.list.get_member(email)
		except ValueError:
			self._raise_nomember(email)
		self.list.add_owner(member.address)

	def is_owner(self, email):
		return self.list.is_owner(email)

	def demote_from_owner(self, email):
		owners = self.list.owners
		if not self.list.is_owner(email):
			raise exceptions.NoMemberException('{} is not an owner address of {}'.format(email, self.fqdn_listname))
		# FIXME: No lock here. Potential race condition
		if len(self.list.owners) == 1:
			raise exceptions.LastOwnerException(email)
		self.list.remove_owner(email)

	def _patched_unsubscribe(self, email, **kwargs):
		# As of mailmanclient=3.3.2, no confirmation for REST-based unsubscribe is send
		# Here, we manually issue a REST call.
		# Remove this function, as soon as this gets fixed in upstream
		data = {k: v for k, v in kwargs.items() if v is not None}
		try:
			path = 'lists/{}/member/{}'.format(self.list_id, email)
			response, answer = self.conn.rest_call(path, data, 'DELETE')
			# Possible responses and answers
			#   HTTP 202: json, i.e. with token
			#   HTTP 204: None-answer, i.e. no confirmation requested
			if response.status_code == 202:
				return answer["token"]
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
			self._raise_nomember(email)
			
	def remove_member_silently(self, email):
		"""Remove member with all roles, no confirmation required. Fails if last owner.

		FIXME: Not really silent. See :func:`~tenca.malinglist.MailingList.remove_member`"""
		return self.remove_member(email, pre_confirmed=None)

	def remove_member(self, email, pre_confirmed=False):
		"""Remove member with all roles. Fails if last owner.

		Attention: As of mailman<3.3.3, the `send_goodbye_message` attribute of a list
		is not exposed using the REST API. Thus, this function is never silent and
		will always send a final notification when a member is successfully removed.
		"""

		if self.list.is_owner(email):
			self.demote_from_owner(email)
		return self._patched_unsubscribe(email, pre_confirmed=pre_confirmed)

	def inject_message(self, sender_address, subject, message):
		raw_text = ("From: {}\n"
		"To: {}\n"
		"Subject: {}\n"
		"\n"
		"{}").format(sender_address, self.fqdn_listname, subject, message)
		in_queue = self.conn.client.queues['in']
		in_queue.inject(self.list_id, raw_text)

	############################################################################
	## Options

	@property
	def notsubscribed_allowed_to_post(self):
		return self.list.settings['default_nonmember_action'] != 'accept'

	@notsubscribed_allowed_to_post.setter
	def notsubscribed_allowed_to_post(self, is_allowed):
		if is_allowed:
			self.list.settings['default_nonmember_action'] = 'accept'
		else:
			self.list.settings['default_nonmember_action'] = settings.DISABLED_NON_MEMBER_ACTION
		self.list.settings.save()

	############################################################################

	@property
	def fqdn_listname(self):
		return self.list.fqdn_listname

	@property
	def list_id(self):
		return self.list.list_id

	@property
	def hashid(self):
		"""Returns a unique hash, that can be used to identify this list"""
		# FIXME: eemaill uses random ids. Make sure, we don't clash
		BAD_B64_CHARS = '+/='

		hashobj = hashlib.sha256()
		hashobj.update((settings.LIST_HASHID_SALT + '$' + self.list_id).encode('ascii'))
		b64 = base64.b64encode(hashobj.digest()).decode('ascii')
		return b64.translate({ord(c): None for c in BAD_B64_CHARS})
