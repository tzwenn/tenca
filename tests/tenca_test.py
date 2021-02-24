import unittest

import urllib.error

from tenca import settings, exceptions
from tenca.connection import Connection

class TencaTest(unittest.TestCase):

	def email(name):
		return '{}@{}'.format(name, settings.TEST_MAIL_DOMAIN)

	def list_id(name):
		return '{}.{}'.format(name, settings.TEST_LIST_DOMAIN)

	def assertSortedListEqual(self, first, second):
		self.assertListEqual(
			list(sorted(first)),
			list(sorted(second))
		)

	def setUp(self):
		self.conn = Connection()

	def clear_testlist(self, listname):
		try:
			self.conn.client.delete_list(self.conn.fqdn_ize(listname))
		except urllib.error.HTTPError as e:
			exceptions.map_http_404(e)
