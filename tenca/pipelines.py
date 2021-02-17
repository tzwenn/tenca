################################################################################
## A list of default functions, that can be overwritten in settings

from . import settings

import urllib.parse

def build_invite_link(mailinglist):
	return urllib.parse.urlunsplit(['http', settings.TEST_DOMAIN, mailinglist.hashid, '', ''])


################################################################################
## Function lookup

import importlib

def get_func(function_string):
	mod_name, func_name = function_string.rsplit('.', 1)
	mod = importlib.import_module(mod_name)
	return getattr(mod, func_name)