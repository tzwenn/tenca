from . import exceptions, settings
from .mailinglist import MailingList

import urllib.error

import mailmanclient

class Connection(object):

	"""A decorator for mailmanclient.Client"""

	def __init__(self):
		self.client = mailmanclient.Client(self.BASE_URL, settings.ADMIN_USER, settings.ADMIN_PASS)
		domains = self.client.domains
		assert len(domains), 1
		self.domain = domains[0]

	def __repr__(self):
		return '<{} on {} for {}>'.format(type(self).__name__, self.BASE_URL, str(self.domain))

	def _wrap_list(self, list):
		return MailingList(self, list)

	@classmethod
	@property
	def BASE_URL(cls):
		return "{}://{}:{}/{}/".format(settings.API_SCHEME, settings.API_HOST, settings.API_PORT, settings.API_VERSION)

	def rest_call(self, path, data=None, method=None):
		return self.client._connection.call(path, data, method)

	def fqdn_ize(self, listname):
		if '@' in listname:
			return listname
		else:
			return '{}@{}'.format(listname, str(self.domain))

	def get_list(self, fqdn_listname):
		return self._wrap_list(self.client.get_list(fqdn_listname))

	def get_list_by_hashid(self, hashid):
		"""Lookup a MailingList by hashid (VERY SLOW!)

		To date, a primary design goal of Tenca is to keep
		all model state only within mailman's backend.

		hashid breaks this, as it is computed from backend and local
		information, but required by the web interface to uniquely
		identify a mailing list.
		Thus, to find a list we iterate OVER THE ENTIRE	MODEL.

		It is STRONLY ADVISED to cache a hashid-to-list_id mapping
		elsewhere to limit calls to this function and check afterwards
		if that list still exists.
		"""
		for list in map(self._wrap_list, self.client.lists):
			if list.hashid == hashid:
				return list
		return None

	def add_list(self, name, creator_email):
		new_list = self.domain.create_list(name)
		wrapped_list = self._wrap_list(new_list)

		wrapped_list.configure_list()
		wrapped_list.add_member_silently(creator_email)
		wrapped_list.promote_to_owner(creator_email)

		return wrapped_list

	def find_lists(self, address, role=None):
		# FIXME: This might be paginated
		try:
			found_lists = self.client.find_lists(address, role)
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
			return []
		return [self._wrap_list(list) for list in found_lists]

	def mark_address_verified(self, address):
		try:
			addr = self.client.get_address(address)
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e, exceptions.NoMemberException)
		else:
			addr.verify()