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
		self.assertDictEqual(
			self.testlist.pending_subscriptions(),
			{token: self.p2_name}
		)

		self.testlist.confirm_subscription(token)
		self.assertMembers([self.creator_name, self.p2_name])
		pending = self.testlist.pending_subscriptions()
		self.assertDictEqual(
			pending,
			{}
		)

	def testNonSilentRemoval(self):
		self.testlist.add_member_silently(self.p2_name)
		token = self.testlist.remove_member(self.p2_name)
		self.assertMembers([self.creator_name, self.p2_name])
		pending = self.testlist.pending_subscriptions()
		## Assertion removed, as of MailmanCore<3.3.3 pending dict will be empty
		# self.assertDictEqual(
		#	pending,
		#	{token: self.p2_name}
		#)

		self.testlist.confirm_subscription(token)
		self.assertMembers([self.creator_name])
		self.assertDictEqual(
			pending,
			{}
		)
