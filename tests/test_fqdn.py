import unittest

from tenca import connection, settings

class FQDNTest(unittest.TestCase):

	base_data = [
		'testlist1',
		'testlist1.foo',
		'testlist1.foo.bar',
	]

	def setUp(self):
		self.conn = connection.Connection()
	
	def testFQDN(self):
		test_data = {
			(base + suffix): (base + '@' + settings.TEST_LIST_DOMAIN)
				for suffix in ('', '.' + settings.TEST_LIST_DOMAIN, '@' + settings.TEST_LIST_DOMAIN)
				for base in self.base_data
		}

		for short_name, fqdn in test_data.items():
			self.assertEqual(self.conn.fqdn_ize(short_name), fqdn)

	def testConnectionInfoInRepr(self):
		info = repr(self.conn)
		self.assertIn(settings.API_HOST, info)
		self.assertIn(str(settings.API_PORT), info)
		self.assertIn(settings.API_VERSION, info)
		self.assertIn(settings.TEST_MAIL_DOMAIN, info)
