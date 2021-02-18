from . import settings
from .connection import Connection

import urllib


testlist_name = 'testlist'
creator_name = 'thecreator@' + settings.TEST_DOMAIN

conn = Connection()
try:
	conn.client.delete_list(conn.fqdn_ize(testlist_name))
except urllib.error.HTTPError:
	pass

testlist = conn.add_list(testlist_name, creator_name)

token = testlist.add_member('person2@' + settings.TEST_DOMAIN)
testlist.confirm_subscription(token)

testlist.inject_message(creator_name, 'A testmail.', 
'''Hi folks,

i just wanted to let you know, that the mail injection works.
Look at the footer :)

Best,
the list creator''')
