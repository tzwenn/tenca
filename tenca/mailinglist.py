from . import settings

import base64
import hashlib

import mailmanclient

class MailingList(object):

	"""A decorator for mailmanclient.restobjects.mailinglist.MailingList"""

	def __init__(self, connection, list):
		self.conn = connection
		self.list = list

	def add_member_silently(self, email):
		"""Subscribe an email address to a mailing list, with no verification send"""
		self.list.subscribe(email, pre_verified=True, pre_confirmed=True)

	def add_member(self, email):
		pass

	def hashid(self):
		"""Returns a unique hash, that can be used to identify this list"""
		# FIXME: Include something, that prevents clashes with legacy eemaill ids
		hashobj = hashlib.sha256()
		hashobj.update(settings.LIST_HASHID_SALT + '$' + self.list.list_id)
		return base64.encode(hashobj.hexdigest)

	def remove_member(self, email):
		self.list.unsubscribe(email)