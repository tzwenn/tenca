from . import exceptions, pipelines, settings, templates

import base64
import hashlib

import mailmanclient


class MailingList(object):

	"""A decorator for mailmanclient.restobjects.mailinglist.MailingList"""

	def __init__(self, connection, list):
		self.conn = connection
		self.list = list

	def __repr__(self):
		return "<{} '{}'>".format(type(self).__name__, str(self.fqdn_listname))

	def add_member_silently(self, email):
		"""Subscribe an email address to a mailing list, with no verification or notification send"""
		self.list.subscribe(email, pre_verified=True, pre_confirmed=True, send_welcome_message=False)

	def add_member(self, email):
		"""Subscribes a user and sends them a confirmation mail

		Returns the authentication token for that subscription.
		"""
		return self.list.subscribe(email)["token"]

	def configure_list(self):
		new_list = self.list
		new_list.settings.update(settings.LIST_DEFAULT_SETTINGS)
		new_list.settings['subject_prefix'] = '[{}] '.format(new_list.settings['list_name'].lower())
		if settings.DEFAULT_OWNER_ADDRESS is not None:
			new_list.settings['owner_address'] = settings.DEFAULT_OWNER_ADDRESS
		new_list.settings['description'] = self.hashid
		new_list.set_template('list:member:regular:footer', templates.http_substitute_url(
			'mail_footer', invite_link=pipelines.get_func(settings.BUILD_INVITE_LINK)(self)
		))
		new_list.settings.save()

	def pending_subscriptions(self):
		return {r['token']: r['email'] for r in self.list.get_requests(token_owner='subscriber')}

	def confirm_subscription(self, token):
		self.list.accept_request(token)

	def promote_to_owner(self, email):
		# Throws ValueError if user not member of mailinglist
		member = self.list.get_member(email)
		self.list.add_owner(member.address)

	def demote_from_owner(self, email):
		owners = self.list.owners
		if not self.list.is_owner(email):
			raise ValueError('{} is not an owner address of {}'.format(email, self.list.fqdn_listname))
		# FIXME: No lock here. Potential race condition
		if len(self.list.owners) == 1:
			raise exceptions.LastOwnerException(email)
		self.list.remove_owner(email)

	def remove_member(self, email):
		"""Remove member with all roles. Fails if last owner"""
		if self.list.is_owner(email):
			self.demote_from_owner(email)
		# FIXME: Is not silent
		self.list.unsubscribe(email)

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
