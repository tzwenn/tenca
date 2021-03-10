from .list_test import ListTest

from tenca import settings
from tenca import exceptions

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
		self.assertDictEqual(
			self.testlist.pending_subscriptions(),
			{}
		)

	def testToggleMembership(self):
		status, token = self.testlist.toggle_membership(self.p2_name)
		self.assertTrue(status)
		self.testlist.confirm_subscription(token)
		self.assertMembers([self.creator_name, self.p2_name])

		status, token = self.testlist.toggle_membership(self.p2_name)
		self.assertFalse(status)
		self.testlist.confirm_subscription(token)
		self.assertMembers([self.creator_name])


	def testCancelPendingAddition(self):
		token = self.testlist.add_member(self.p2_name)
		self.testlist.cancel_pending_subscription(token)
		self.assertMembers([self.creator_name])
		self.assertDictEqual(
			self.testlist.pending_subscriptions(),
			{}
		)

	def testNonExistentRequests(self):
		with self.assertRaises(exceptions.NoSuchRequestException):
			self.testlist.confirm_subscription('Does Not Exists')
		with self.assertRaises(exceptions.NoSuchRequestException):
			self.testlist.cancel_pending_subscription('Does Not Exists')

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

	def testCancelOnReRequest(self):
		old_setting = settings.RETRY_CANCELS_PENDING_SUBSCRIPTION
		settings.RETRY_CANCELS_PENDING_SUBSCRIPTION = True
		try:
			token = self.testlist.add_member(self.p2_name)
			self.assertMembers([self.creator_name])
			self.assertDictEqual(
				self.testlist.pending_subscriptions(),
				{token: self.p2_name}
			)
			token2 = self.testlist.add_member(self.p2_name)
			self.assertMembers([self.creator_name])
			self.assertDictEqual(
				self.testlist.pending_subscriptions(),
				{token2: self.p2_name}
			)
			self.testlist.confirm_subscription(token2)
			self.assertMembers([self.creator_name, self.p2_name])
		finally:
			settings.RETRY_CANCELS_PENDING_SUBSCRIPTION = old_setting
