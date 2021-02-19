from . import settings
from .connection import Connection

import urllib


testlist_name = 'testlist'
creator_name = 'thecreator@' + settings.TEST_DOMAIN
p2_name = 'person2@' + settings.TEST_DOMAIN

conn = Connection()
try:
	conn.client.delete_list(conn.fqdn_ize(testlist_name))
except urllib.error.HTTPError:
	pass

testlist = conn.add_list(testlist_name, creator_name)
# testlist.add_member_silently(p2_name)
