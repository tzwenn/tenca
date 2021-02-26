from . import exceptions, pipelines, settings
from .mailinglist import MailingList
from .hash_storage import NotInStorageError

import itertools
import urllib.error

import mailmanclient

class Connection(object):

	"""A decorator for mailmanclient.Client"""

	def __init__(self, hash_storage_cls=None):
		"""Creates a new connection to Mailman's REST API.

		Can be provided with a subclass of tenca.HashStorage to lookup
		scrambled hashes, identifying a mailing list in the invite links.

		If hash_storage_cls is None, the class specified in
		settings.HASH_STORAGE_CLASS will be used.
		"""
		self.client = mailmanclient.Client(self.BASE_URL, settings.ADMIN_USER, settings.ADMIN_PASS)
		domains = self.client.domains
		assert len(domains), 1
		self.domain = domains[0]
		if hash_storage_cls is None:
			hash_storage_cls = pipelines.get_func(settings.HASH_STORAGE_CLASS)
		assert hash_storage_cls is not None
		self.hash_storage = hash_storage_cls(self)

	def __repr__(self):
		return '<{} on {} for {}>'.format(type(self).__name__, self.BASE_URL, str(self.domain))

	def _wrap_list(self, list, skip_hash_id=False, hash_id=None):
		if hash_id is None:
			try:
				hash_id = None if skip_hash_id else self.hash_storage.list_hash(list)
			except NotInStorageError:
				hash_id = None
		return MailingList(self, list, hash_id)

	@classmethod
	@property
	def BASE_URL(cls):
		return "{}://{}:{}/{}/".format(settings.API_SCHEME, settings.API_HOST, settings.API_PORT, settings.API_VERSION)

	def rest_call(self, path, data=None, method=None):
		return self.client._connection.call(path, data, method)

	def fqdn_ize(self, listname):
		if '@' in listname:
			return listname
		domain_str = '.' + str(self.domain)
		if listname.endswith(domain_str):
			listname = listname.rsplit(domain_str, 1)[0]
		return '{}@{}'.format(listname, str(self.domain))

	def get_list(self, fqdn_listname):
		try:
			return self._wrap_list(self.client.get_list(fqdn_listname))
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
			return None

	def get_list_by_hash_id(self, hash_id):
		try:
			return self._wrap_list(self.hash_storage.get_list(hash_id), hash_id=hash_id)
		except NotInStorageError:
			# TODO: Discard hash if in storage? What's the fastest way?
			return None

	def add_list(self, name, creator_email):
		new_list = self.domain.create_list(name)

		wrapped_list = self._wrap_list(new_list, skip_hash_id=True)
		wrapped_list.configure_list()

		proposals = (wrapped_list.propose_hash_id(round) for round in itertools.count())
		for proposed_hash_id in proposals:
			if proposed_hash_id not in self.hash_storage:
				wrapped_list.hash_id = proposed_hash_id
				self.hash_storage.store_list(proposed_hash_id, new_list)
				break
		wrapped_list.configure_templates()

		wrapped_list.add_member_silently(creator_email)
		wrapped_list.promote_to_owner(creator_email)

		return wrapped_list

	def delete_list(self, listname, silent_fail=True, retain_hash=False):
		if not retain_hash:
			l = self.get_list(self.fqdn_ize(listname))
			if l is None:
				if silent_fail:
					return
				raise exceptions.TencaException("No such list")
			fqdn = l.fqdn_listname
			self.hash_storage.delete_hash_id(l.hash_id)
		else:
			fqdn = self.fqdn_ize(listname)
		try:
			self.client.delete_list(fqdn)
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e, None if silent_fail else exceptions.TencaException)

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