from . import settings
from .connection import Connection

testlist_name = 'testlist'
creator_name = 'thecreator@' + settings.TEST_MAIL_DOMAIN
p2_name = 'person2@' + settings.TEST_MAIL_DOMAIN

conn = Connection()
conn.delete_list(testlist_name)

testlist = conn.add_list(testlist_name, creator_name)
# testlist.add_member_silently(p2_name)
