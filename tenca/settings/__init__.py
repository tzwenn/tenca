from tenca.settings.defaults import *

try:
	from local_tenca_settings import *
except ImportError: # pragma: no cover
	import sys
	sys.stderr.write('Could not import your "local_tenca_settings.py" file.\n')
	sys.stderr.write('Try setting your PYTHONPATH accordingly.\n')

class TemporarySettingsChange(object):

	def __init__(self, **kwargs):
		self.settings_diff = kwargs

	def __enter__(self):
		self.old_settings = {}
		for setting_name, temp_setting in self.settings_diff.items():
			self.old_settings[setting_name] = globals()[setting_name]
			globals()[setting_name] = temp_setting

	def __exit__(self, exc_type, exc_value, traceback):
		for setting_name, old_setting in self.old_settings.items():
			globals()[setting_name] = old_setting