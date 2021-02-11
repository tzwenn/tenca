from .connection import Connection

import sys

testlist_name = 'testlist'

conn = Connection()
try:
	conn.client.delete_list(conn.fqdn_ize(testlist_name))
except:
	pass

testlist = conn.add_list(testlist_name, 'user@example.com')
