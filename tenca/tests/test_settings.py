import unittest

class TestSettingsChanger(unittest.TestCase):

	def testSettingsChanger(self):
		from tenca import settings
		old_port = settings.API_PORT
		new_port = old_port + 1
		with settings.TemporarySettingsChange(API_PORT=new_port):
			self.assertEqual(settings.API_PORT, new_port)
		self.assertEqual(settings.API_PORT, old_port)

	def testSettingsChangerMultiple(self):
		from tenca import settings
		old_port = settings.API_PORT
		new_port = old_port + 1

		old_version = settings.API_VERSION
		new_version = '99.99'

		with settings.TemporarySettingsChange(API_PORT=new_port, API_VERSION=new_version):
			self.assertEqual(settings.API_PORT, new_port)
			self.assertEqual(settings.API_VERSION, new_version)
		self.assertEqual(settings.API_PORT, old_port)
		self.assertEqual(settings.API_VERSION, old_version)
