## Define these settings in your settings_local.py
# ADMIN_USER =
# ADMIN_PASS =

# You can also overwrite any other settings

API_HOST = 'localhost'
API_PORT = 9001

API_VERSION = 3.0
API_SCHEME = 'http'

# In case you have equivalent domains in your emails,
# you can enlist equivalent tuples here
EMAIL_DOMAIN_ALIASES = [
	# ('example.com', 'foo.example.com')
]

# Used to update the default settings for new mailing lists
LIST_DEFAULT_SETTINGS = {
	'advertised': False
}

# If not None, this will override the listname-owner@lists.example.com
DEFAULT_OWNER_ADDRESS = None

# Invite links are a hash of each mailing list name. This is the salt
LIST_HASHID_SALT = "ChangeMe"

# Use this domain for tests in __main__.py or the unittests
TEST_DOMAIN = 'example.com'

# A running tenca.templateserver for delivering footers/etc to mailman
TEMPLATE_SERVER_ADDRESS = 'http://localhost:8080'

try:
	from settings_local import *
except ImportError:
	pass