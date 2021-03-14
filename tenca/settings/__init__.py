from tenca.settings.defaults import *

try:
	from local_tenca_settings import *
	LOCAL_SETTINGS_FOUND = True
except ImportError:
	LOCAL_SETTINGS_FOUND = False

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


def warn_on_missing_local_settings():
	if not LOCAL_SETTINGS_FOUND:
		import sys
		sys.stderr.write('Could not import your "local_tenca_settings.py" file.\n')
		sys.stderr.write('Try setting your PYTHONPATH accordingly.\n')


def load_from_module(module, prefix='TENCA_'):
	relevant_settings = ((name.split(prefix, 1)[1], name) for name in dir(module) if name.startswith(prefix))
	for tenca_name, remote_name in relevant_settings:
		globals()[tenca_name] = getattr(module, remote_name)
