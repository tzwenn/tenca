## Define these settings in your local_tenca_settings.py
# ADMIN_USER =
# ADMIN_PASS =

# You can also overwrite any other settings
API_HOST = 'localhost'
API_PORT = 9001

API_VERSION = '3.1'
API_SCHEME = 'http'

# Used to update the default settings for new mailing lists
LIST_DEFAULT_SETTINGS = {
	# 'key': value
}

# What happens to messages when non-members post while this is not enabled? ('discard'/'reject')
DISABLED_NON_MEMBER_ACTION = 'reject'

# What happens to messages when moderated/blocked members post? ('discard'/'reject')
BLOCKED_MEMBER_ACTION = 'reject'

# Does a re-request with the same e-mail cancel the previous one?
RETRY_CANCELS_PENDING_SUBSCRIPTION = True

# Invite links are a hash of each mailing list name. This is the salt
LIST_HASH_ID_SALT = 'ChangeMe'

# If you do not want to have reproducible invite links, change this to True
USE_RANDOM_LIST_HASH = False

# Class to lookup hash_id->list_id mappings
HASH_STORAGE_CLASS = 'tenca.hash_storage.DictCachedDescriptionStorage'

# Emails in the unittests or __main__.py will end in this domain
TEST_MAIL_DOMAIN = 'example.com'

# List-Addresses in the unittests or __main__.py will end in this domain
TEST_LIST_DOMAIN = 'lists.example.com'

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

# Enable for mailman>=3.3.3 to allow silent removal of users from lists
DISABLE_GOODBYE_MESSAGES = False
