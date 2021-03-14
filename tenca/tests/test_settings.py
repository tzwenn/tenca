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

	def testModuleLoad(self):
		from tenca import settings
		from . import data_test_settings
		settings.load_from_module(data_test_settings)
		
		self.assertFalse(hasattr(settings, 'NOT_APPLIED_OPTION'))
		self.assertFalse(hasattr(settings, 'DIFFERENT_PREFIXAPPLIEDOPTION'))
		self.assertTrue(hasattr(settings, 'APPLIED_OPTION'))
		self.assertEqual(settings.APPLIED_OPTION, 'Placeholder')

		settings.load_from_module(data_test_settings, prefix='DIFFERENT_PREFIX')
		self.assertTrue(hasattr(settings, 'APPLIEDOPTION'))
		self.assertEqual(settings.APPLIEDOPTION, 'Placeholder')
