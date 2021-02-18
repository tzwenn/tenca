import unittest

from .listtest import ListTest

from tenca import exceptions

class TestRoles(ListTest):

	p3_name = ListTest.email('person3')
	nh_name = ListTest.email('not_here')

	def testSilentAddition(self):
		self.testlist.add_member_silently(self.p2_name)
		self.testlist.add_member_silently(self.p3_name)
		self.assertMembers([self.creator_name, self.p2_name, self.p3_name])

	def testRemoval(self):
		self.testSilentAddition()
		self.testlist.remove_member_silently(self.p2_name)
		self.assertMembers([self.creator_name, self.p3_name])
		with self.assertRaises(exceptions.NoMemberException):
			self.testlist.remove_member_silently(self.nh_name)
		with self.assertRaises(exceptions.LastOwnerException):
			self.testlist.remove_member_silently(self.creator_name)

	def testPromotionAndDemotion(self):
		self.testSilentAddition()
		self.assertMembers([self.creator_name], "owners")
		self.testlist.promote_to_owner(self.p2_name)
		self.assertMembers([self.creator_name, self.p2_name], "owners")

	def testDemotion(self):
		self.testPromotionAndDemotion()
		self.testlist.remove_member_silently(self.creator_name)
		self.assertMembers([self.p2_name], "owners")
		with self.assertRaises(exceptions.NoMemberException):
			self.testlist.demote_from_owner(self.p3_name)

if __name__ == '__main__':
	unittest.main()