class TencaException(Exception):
	pass

class NoMemberException(TencaException):
	pass

class NoSuchRequestException(TencaException):

	def __init__(self, list, token):
		super().__init__('No pending request {} on list <{}>.'.format(token, list.fqdn_listname))

class LastOwnerException(TencaException):
	
	def __init__(self, email):
		super().__init__('User <{}> is the last owner. Cannot remove.'.format(email))
