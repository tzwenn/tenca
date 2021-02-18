import unittest
import urllib

from tenca.connection import Connection
from tenca import exceptions, settings

class ListTest(unittest.TestCase):

	testlist_name = 'testlist'

	def email(name):
		return '{}@{}'.format(name, settings.TEST_DOMAIN)

	creator_name = email('thecreator')
	p2_name = email('person2')

	def addresses(self, memberlist):
		return [str(member.address) for member in memberlist]

	def assertSortedListEqual(self, first, second):
		self.assertListEqual(
			list(sorted(first)),
			list(sorted(second))
		)

	def assertMembers(self, memberlist, attr_name="members"):
		attr = getattr(self.testlist.list, attr_name)
		self.assertSortedListEqual(
			memberlist,
			self.addresses(attr)
		)


	def clear_testlist(self):
		try:
			self.conn.client.delete_list(self.conn.fqdn_ize(self.testlist_name))
		except urllib.error.HTTPError:
			pass

	def setUp(self):
		self.conn = Connection()
		self.clear_testlist()
		self.testlist = self.conn.add_list(self.testlist_name, self.creator_name)

	def tearDown(self):
		self.clear_testlist()