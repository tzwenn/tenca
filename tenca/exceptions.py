class TencaException(Exception):
	pass

class NoMemberException(TencaException):
	pass

class LastOwnerException(TencaException):
	
	def __init__(self, email):
		super().__init__('User <{}> is the last owner. Cannot remove.'.format(email))
