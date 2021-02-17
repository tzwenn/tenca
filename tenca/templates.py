import string
import urllib.parse


mail_footer = string.Template(r"""
_________________________________________________________________
Share this link to invite more people or click to unsubscribe:
$invite_link""")

confirmation_message = string.Template(
r"""Welcome to $fqdn_listname

Please confirm your *$action_name*:
$action_link

If you did not request this, please report abuse by visiting the following link:
$action_abuse_link

Enjoy our service!""")

creation_message = string.Template(
r"""Thanks for your sign-up!

This is your new list:
$fqdn_listname

Share the following URL to people that you want to invite to the list:
$invite_link

Have fun!""")


################################################################################


templates_dict = {
	name: var for name, var in locals().items() if isinstance(var, string.Template)
}

def substitute(name, **kwargs):
	if not name in templates_dict:
		raise KeyError('No templated named "{}"'.format(name))
	return templates_dict[name].substitute(**kwargs)

def http_substitute_url(name, **kwargs):
	# Test substitution. Throws exceptions that otherwise show in tenca.templateserver
	_test_substitution = substitute(name, **kwargs)

	# Hide settings import from tenca.templateserver
	from . import settings

	return urllib.parse.urlunsplit(['', # We will need to lstrip the scheme
		settings.TEMPLATE_SERVER_ADDRESS, name, 
		urllib.parse.urlencode(kwargs), '']).lstrip('//')