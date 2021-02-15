from . import settings
from .connection import Connection

import urllib


testlist_name = 'testlist'
creator_name = 'thecreator@{}'.format(settings.TEST_DOMAIN)

conn = Connection()
try:
	conn.client.delete_list(conn.fqdn_ize(testlist_name))
except urllib.error.HTTPError:
	pass

testlist = conn.add_list(testlist_name, creator_name)
