from . import exceptions, settings
from .connection import Connection

import sys
import urllib

testlist_name = 'testlist'
creator_name = 'thecreator'
p2_name = 'person2'
p3_name = 'person3'
nh_name = 'not_here'

def email(name):
	return '{}@{}'.format(name, settings.TEST_DOMAIN)

conn = Connection()
try:
	conn.client.delete_list(conn.fqdn_ize(testlist_name))
except urllib.error.HTTPError:
	pass

testlist = conn.add_list(testlist_name, email(creator_name))

def print_members_and_owners():
	print('Members:', *(m.address for m in testlist.list.members))
	print('Owners:', *(m.address for m in testlist.list.owners))
	print('----------------------------------------------------')

testlist.add_member_silently(email(p2_name))
testlist.add_member_silently(email(p3_name))
print_members_and_owners()

testlist.promote_to_owner(email(p2_name))
print_members_and_owners()

testlist.remove_member(email(creator_name))
print_members_and_owners()

try:
	testlist.demote_from_owner(email(p2_name))
except exceptions.LastOwnerException:
	print("Correctly prevented demotion of last owner")
else:
	assert False

try:
	testlist.remove_member(email(nh_name))
except ValueError:
	print("Correctly prevented removal of non-existent user")
else:
	assert False
