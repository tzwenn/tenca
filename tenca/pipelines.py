################################################################################
## A list of default functions, that can be overwritten in settings

from . import settings

import urllib.parse

def build_invite_link(mailinglist):
	return urllib.parse.urlunsplit([settings.WEB_UI_SCHEME, settings.WEB_UI_HOSTNAME, mailinglist.hash_id, '', ''])


def build_action_link(mailinglist, token, action='confirm'):
	return urllib.parse.urlunsplit([settings.WEB_UI_SCHEME, settings.WEB_UI_HOSTNAME,
		'/'.join((action, mailinglist.list_id, token)),
		'', ''])

def build_action_abuse_link(mailinglist, token):
	return build_action_link(mailinglist, token, 'report')

################################################################################
## Function lookup

import importlib

def get_func(function_string):
	mod_name, func_name = function_string.rsplit('.', 1)
	mod = importlib.import_module(mod_name)
	return getattr(mod, func_name)

def call_func(function_string, *args, **kwargs):
	func = get_func(function_string)
	return func(*args, **kwargs)
