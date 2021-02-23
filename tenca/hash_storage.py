from . import exceptions

from abc import ABCMeta, abstractmethod
import urllib.error

import mailmanclient

class NotInStorageError(exceptions.TencaException):
	pass

class HashStorage(object, metaclass=ABCMeta):
	"""Abstract base class to lookup MailingLists by a random (hash) identifier.

	Allows you to find and store MailingList objects by scrambled hash_ids.
	Under the hood you can plug any key-value store from string to string,
	to store hash_id->list_id mappings by re-implementing get_list_id/store_list_id.

	HashStorage will then use an open tenca.Connection to construct a matching list-object.
	"""

	def __init__(self, connection):
		self.conn = connection

	def _raw_conn_getlist(self, list_id: str) -> mailmanclient.MailingList:
		try:
			return self.conn.client.get_list(list_id)
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e) # raise below
		raise NotInStorageError()

	def get_list(self, hash_id: str) -> mailmanclient.MailingList:
		"""Returns a mailmanclient.MailingList object for hash_id
		
		Only re-implement in rare cases, use tenca.Connection.get_list instead
		to receive a properly wrapped tenca.MailingList object.
		"""
		list_id = self.get_list_id(hash_id)
		if list_id is None:
			raise NotInStorageError()

		return self._raw_conn_getlist(list_id)
	
	def store_list(self, hash_id: str, list: mailmanclient.MailingList):
		"""Saves the hash_id for this mailmanclient.MailingList object"""
		self.store_list_id(hash_id, list.list_id)

	def list_hash(self, list: mailmanclient.MailingList):
		"""Returns the hash_id for this mailmanclient.MailingList object"""
		return self.get_hash_id(list.list_id)

	def __contains__(self, hash_id: str):
		"""Check if hash_id is present in this storage"""
		return hash_id in self.keys()

	@abstractmethod
	def get_list_id(self, hash_id: str) -> str:
		"""Returns a list id by `hash_id`.
		
		Raises `NotInStorageError`, if no such list exists
		"""
		pass

	@abstractmethod
	def store_list_id(self, hash_id: str, list_id: str):
		"""Stores list_id by hash_id."""
		pass

	@abstractmethod 
	def get_hash_id(self, list_id: str) -> str:
		"""Reverse operation of `get_list_id`.
		
		Raises `NotInStorageError`, if no such list exists.
		"""
		pass

	@abstractmethod
	def keys(self):
		"""Returns an iterator over all known hashes"""
		pass


class VolatileDictHashStorage(HashStorage):
	"""Non-persistent hash_id -> list_id storage in a dictionary.
	
	Forgotten as soon, as the program ends. Finds no lists created
	before. Only suitable for testing.
	"""

	def __init__(self, connection):
		super().__init__(connection)
		self._d = {}

	def __contains__(self, hash_id):
		return hash_id in self._d

	def get_list_id(self, hash_id):
		try:
			return self._d[hash_id]
		except KeyError:
			raise NotInStorageError()

	def get_hash_id(self, list_id):
		try:
			return next(hash_id for hash_id, lid in self._d.items() if lid == list_id)
		except StopIteration:
			raise NotInStorageError()

	def store_list_id(self, hash_id, list_id):
		self._d[hash_id] = list_id

	def keys(self):
		return self._d.keys()


class MailmanDescriptionHashStorage(HashStorage):
	"""Uses the (short) Description field of mailman to lookup/store
	hash_id -> list_id mappings.

	Attention: USES SLOW, LINEAR LOOKUP!
	It also breaks LSP, as saving a hash for non-existent lists silently
	discards that value and not retains it as suggested by the API.
	"""

	PREFIX = "tenca!"

	def _is_hash_id(self, dsc):
		return dsc.startswith(self.PREFIX)

	def _split_hash_id(self, dsc):
		return dsc.split(self.PREFIX, 1)[1]

	def _get_dsc(self, list):
		return list.settings['description']
	
	def _set_dsc(self, list, dsc):
		list.settings['description'] = dsc
		list.settings.save()

	def get_list(self, hash_id):
		for list in self.conn.client.lists:
			dsc = self._get_dsc(list)
			if self._is_hash_id(dsc) and self._split_hash_id(dsc) == hash_id:
				return list
		raise NotInStorageError()

	def store_list(self, hash_id, list):
		self._set_dsc(list, self.PREFIX + hash_id)

	def list_hash(self, list):
		dsc = list.settings['description']
		if not self._is_hash_id(dsc):
			raise NotInStorageError()
		return self._split_hash_id(dsc)

	def get_list_id(self, hash_id):
		return self.get_list(hash_id).list_id

	def store_list_id(self, hash_id, list_id):
		try:
			self.store_list(hash_id,
				self._raw_conn_getlist(list_id))
		except NotInStorageError:
			pass

	def get_hash_id(self, list_id):
		return self.list_hash(self._raw_conn_getlist(list_id))

	def keys(self):
		descriptions = (self._get_dsc(l) for l in self.conn.client.lists)
		return (self._split_hash_id(dsc) for dsc in descriptions if self._is_hash_id(dsc))


class TwoLevelHashStorage(HashStorage):
	"""Uses a two-level storage, e.g. first a dict (hot), then mailman description field (cold).

	The hot storage (level 1) must be a subset of the cold storage (level 2).
	"""

	@classmethod
	def factory(cls, l1_class, l2_class):
		return lambda connection: cls(connection, l1_class, l2_class)

	def __init__(self, connection, class1, class2):
		super().__init__(connection)
		self.l1 = class1(connection)
		self.l2 = class2(connection)

	def __contains__(self, hash_id):
		return hash_id in self.l1 or hash_id in self.l2

	def get_list_id(self, hash_id):
		try:
			return self.l1.get_list_id(hash_id)
		except NotInStorageError:
			list_id = self.l2.get_list_id(hash_id)
			self.l1.store_list_id(list_id)
			return list_id
		raise NotInStorageError

	def store_list_id(self, hash_id, list_id):
		"""Stores list_id by hash_id in both storages.
		
		Attention: This is no atomic transaction!
		"""
		# First store l2, so that subset-relation is more likely to be kept
		self.l2.store_list_id(hash_id, list_id)
		self.l1.store_list_id(hash_id, list_id)

	def get_hash_id(self, list_id):
		try:
			return self.l1.get_hash_id(list_id)
		except NotInStorageError:
			hash_id = self.l2.get_hash_id(list_id)
			self.l1.store_list_id(hash_id, list_id)
			return hash_id

	def keys(self, l2_only=False):
		result = set(self.l2.keys())
		if not l2_only:
			result.union(set(self.l1.keys()))

		return iter(result)
		

DictCachedDescriptionStorage = TwoLevelHashStorage.factory(VolatileDictHashStorage, MailmanDescriptionHashStorage)