import unittest

from tenca.connection import Connection
from tenca import exceptions, settings

import sys
import urllib


class TestRoles(unittest.TestCase):

	testlist_name = 'testlist'

	def email(name):
		return '{}@{}'.format(name, settings.TEST_DOMAIN)

	creator_name = email('thecreator')
	p2_name = email('person2')
	p3_name = email('person3')
	nh_name = email('not_here')

	def clear_testlist(self):
		try:
			self.conn.client.delete_list(self.conn.fqdn_ize(self.testlist_name))
		except urllib.error.HTTPError:
			pass

	def addresses(self, memberlist):
		return [str(member.address) for member in memberlist]

	def assertSortedListEqual(self, first, second):
		self.assertListEqual(
			list(sorted(first)),
			list(sorted(second))
		)

	def setUp(self):
		self.conn = Connection()
		self.clear_testlist()
		self.testlist = self.conn.add_list(self.testlist_name, self.creator_name)

	def testAddition(self):
		self.testlist.add_member_silently(self.p2_name)
		self.testlist.add_member_silently(self.p3_name)
		self.assertSortedListEqual(
			[self.creator_name, self.p2_name, self.p3_name],
			self.addresses(self.testlist.list.members)
		)

	def testRemoval(self):
		self.testAddition()
		self.testlist.remove_member(self.p2_name)
		self.assertSortedListEqual(
			[self.creator_name, self.p3_name],
			self.addresses(self.testlist.list.members)
		)
		with self.assertRaises(ValueError):
			self.testlist.remove_member(self.nh_name)
		with self.assertRaises(exceptions.LastOwnerException):
			self.testlist.remove_member(self.creator_name)

	def testPromotionAndDemotion(self):
		self.testAddition()
		self.assertSortedListEqual(
			[self.creator_name],
			self.addresses(self.testlist.list.owners)
		)
		self.testlist.promote_to_owner(self.p2_name)
		self.assertSortedListEqual(
			[self.creator_name, self.p2_name],
			self.addresses(self.testlist.list.owners)
		)

	def testDemotion(self):
		self.testPromotionAndDemotion()
		self.testlist.remove_member(self.creator_name)
		self.assertSortedListEqual(
			[self.p2_name],
			self.addresses(self.testlist.list.owners)
		)

	def tearDown(self):
		self.clear_testlist()

if __name__ == '__main__':
	unittest.main()