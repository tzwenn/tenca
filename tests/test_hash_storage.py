from .tencatest import TencaTest

from tenca.connection import Connection
from tenca.hash_storage import *

__all__ = ['VolatileDictHashStorageTest', 'MailmanDescriptionHashStorageTest', 'DictCachedDescriptionStorageTest']


class DisabledHashStorage(HashStorage):
	"""No storing at all. Disables hash-lookup"""

	def get_list(self, hash_id):
		raise NotInStorageError()

	def store_list(self, hash_id, list):
		pass

	def list_hash(self, list):
		return None
	
	def __contains__(self, hash_id):
		return False

	def get_list_id(self, hash_id):
		raise NotInStorageError()

	def store_list_id(self, hash_id, list_id):
		pass

	def get_hash_id(self, list_id):
		raise NotInStorageError

	def hashes(self):
		return iter([])


class HiddenFromTestRunner(object):

	class HashStorageTest(TencaTest):

		StorageClass = DisabledHashStorage

		# Assumes stable hash_id creation
		test_data = {
			# listname: hash_id
			TencaTest.list_id('list_a'): 'ALongLookingHashId1',
			TencaTest.list_id('list_b'): 'ALongLookingHashId2',
			TencaTest.list_id('list_c'): 'ALongLookingHashId3',
			}

		def setUp(self):
			self.conn = Connection(DisabledHashStorage)
			self.hash_storage = self.StorageClass(self.conn)

			for listname in self.test_data:
				self.clear_testlist(listname)

		def storeTestData(self):
			for list_id, hash_id in self.test_data.items():
				self.hash_storage.store_list_id(hash_id, list_id)

		def testStoreAndRetrieveIds(self):
			self.storeTestData()
			for list_id, hash_id in self.test_data.items():
				self.assertEqual(
					list_id,
					self.hash_storage.get_list_id(hash_id))
				self.assertEqual(
					hash_id,
					self.hash_storage.get_hash_id(list_id)
				)

		def testHashList(self):
			self.storeTestData()
			self.assertSortedListEqual(
				list(self.test_data.values()),
				list(self.hash_storage.hashes())
			)

		def testContains(self):
			self.storeTestData()	
			for hash_id in self.test_data.values():
				self.assertTrue(hash_id in self.hash_storage)

		def testNotInStorage(self):
			self.assertFalse('Invalid_Hash' in self.hash_storage)
			with self.assertRaises(NotInStorageError):
				self.hash_storage.get_list_id('Invalid_Hash')
			with self.assertRaises(NotInStorageError):
				self.hash_storage.get_list('Invalid_Hash')
			with self.assertRaises(NotInStorageError):
				self.hash_storage.get_hash_id('Invalid_ListName')

		def tearDown(self):
			for listname in self.test_data:
				self.clear_testlist(listname)


class VolatileDictHashStorageTest(HiddenFromTestRunner.HashStorageTest):
	StorageClass = VolatileDictHashStorage


class MailmanDescriptionHashStorageTest(HiddenFromTestRunner.HashStorageTest):
	StorageClass = MailmanDescriptionHashStorage

	def setUp(self):
		super().setUp()
		# MailmanDescriptionHashStorage requires lists to be
		# present in the Mailman backend
		for list_id in self.test_data:
			self.conn.domain.create_list(list_id)

	def assertIsSubset(self, sub, super):
		self.assertTrue(
			sub.issubset(super)
		)

	def testHashList(self):
		# For reasons, we do not want to drop all
		# lists on the current running Mailman instance.
		# So, do a subset test instead.
		self.storeTestData()
		self.assertIsSubset(
			set(self.test_data.values()),
			set(self.hash_storage.hashes())
		)


class DictCachedDescriptionStorageTest(MailmanDescriptionHashStorageTest):
	StorageClass = DictCachedDescriptionStorage