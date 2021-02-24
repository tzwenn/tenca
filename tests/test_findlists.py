from .tenca_test import TencaTest

class TestFindLists(TencaTest):

	test_data = {
		# listname: ([creator, *other_owners], [*other_members])
		"list_a": (['thecreator'], []),
		"list_b": (['thecreator', 'person2'], ['person3']),
		"list_c": (['person2'], ['thecreator', 'person3']),
	}

	def email(self, name):
		return TencaTest.email(name)

	def plainNames(self, lists):
		return [list.fqdn_listname.split('@', 1)[0] for list in lists]

	def findLists(self, name, role):
		return self.plainNames(self.conn.find_lists(self.email(name), role))

	def assertFindLists(self, name, role, expected):
		self.assertSortedListEqual(
			expected,
			self.findLists(name, role)
		)

	def setUp(self):
		super().setUp()
		for listname, (owners, members) in self.test_data.items():
			creator, owners = owners[0], owners[1:]
			# Clear in case it existed
			self.clear_testlist(listname)
			newlist = self.conn.add_list(listname, self.email(creator))
			for address in set(owners + members):
				newlist.add_member_silently(self.email(address))
			for address in owners:
				newlist.promote_to_owner(self.email(address))

	def testEmptyListsOfNobody(self):
		self.assertFindLists('nobody', 'member', [])
		self.assertFindLists('nobody', 'owner', [])

	def testPerson3IsSomeMemberButNoOwner(self):
		self.assertGreaterEqual(
			len(self.findLists('person3', 'member')), 
			1)
		self.assertFindLists('person3', 'owner', [])

	def testCreatorOnEveryLists(self):
		self.assertFindLists('thecreator', 'owner',
			['list_a', 'list_b'])
		self.assertFindLists('thecreator', 'member',
			self.test_data.keys())

	def tearDown(self):
		super().tearDown()
		for listname in self.test_data:
			self.clear_testlist(listname)