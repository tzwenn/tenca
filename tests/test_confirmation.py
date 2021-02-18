from .listtest import ListTest

class TestConfirmation(ListTest):

	def testHasSubscriptionToken(self):
		token = self.testlist.add_member(self.p2_name)
		self.assertDictEqual(
			{token: self.p2_name},
			self.testlist.pending_subscriptions()
		)

	def testNonSilentAddition(self):
		token = self.testlist.add_member(self.p2_name)
		self.assertMembers([self.creator_name])
		self.testlist.confirm_subscription(token)
		self.assertMembers([self.creator_name, self.p2_name])
