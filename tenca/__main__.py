from . import settings
from .connection import Connection

testlist_name = 'testlist'
creator_name = 'thecreator@' + settings.TEST_MAIL_DOMAIN
p2_name = 'person2@' + settings.TEST_MAIL_DOMAIN

conn = Connection()