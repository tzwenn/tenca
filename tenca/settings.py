## Define these settings in your settings_local.py
# ADMIN_USER =
# ADMIN_PASS =

# You can also overwrite any other settings

API_HOST = 'localhost'
API_PORT = 9001

API_VERSION = '3.1'
API_SCHEME = 'http'

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

# Use this domain for default pipelines (confirmation links, etc.)
WEB_UI_HOSTNAME = 'lists.example.com'

# Use this scheme for default pipelines (confirmation links, etc.)
WEB_UI_SCHEME = 'https'

# A running tenca.templateserver for delivering footers/etc to mailman
TEMPLATE_SERVER_ADDRESS = 'http://localhost:8080'

# The name of a python function called to create invite links for MailingList objects
BUILD_INVITE_LINK = 'tenca.pipelines.build_invite_link'

# The name of a python function called to create acceptance links for requests
BUILD_ACTION_LINK = 'tenca.pipelines.build_action_link'

# The name of a python function called to create report links for wrongly created requests
BUILD_ACTION_ABUSE_LINK = 'tenca.pipelines.build_action_abuse_link'

try:
	from settings_local import *
except ImportError:
	pass