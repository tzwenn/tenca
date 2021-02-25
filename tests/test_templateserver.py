import tenca.settings
import tenca.templates

import http
import unittest
import urllib.error
import urllib.parse
import urllib.request

class TemplateRequestTest(unittest.TestCase):

	def url(self, path):
		return '{}/{}'.format(tenca.settings.TEMPLATE_SERVER_ADDRESS, path)

	def open(self, path, **kwargs):
		fragments = urllib.parse.urlencode(kwargs)
		if fragments:
			fragments = '?' + fragments
		return urllib.request.urlopen(self.url(path) + fragments)

	def read(self, url):
		return urllib.request.urlopen(url).read().decode('utf-8')

	def testNonExistentTemplateGives404(self):
		with self.assertRaises(urllib.error.HTTPError):
			self.open('no_such_template')
		try:
			self.open('no_such_template')
		except urllib.error.HTTPError as e:
			self.assertEqual(e.code, http.HTTPStatus.NOT_FOUND.value)

	def testNonExistentTemplate(self):
		with self.assertRaises(KeyError):
			tenca.templates.substitute('no_such_template')

	def testNonExistentTemplateGives404(self):
		with self.assertRaises(urllib.error.HTTPError):
			self.open('no_such_template')
		try:
			self.open('no_such_template')
		except urllib.error.HTTPError as e:
			self.assertEqual(e.code, http.HTTPStatus.NOT_FOUND.value)

	def testMissingArgumentGives400(self, **kwargs):
		with self.assertRaises(urllib.error.HTTPError):
			self.open('mail_footer')
		try:
			self.open('mail_footer')
		except urllib.error.HTTPError as e:
			self.assertEqual(e.code, http.HTTPStatus.BAD_REQUEST.value)

	def testMissingArgumentGives400DespiteTooMuchContent(self):
		self.testMissingArgumentGives400(unused_key='Unused value')

	def testAllTemplates(self):
		template_keys = (
			'invite_link',
			'fqdn_listname',
			'action_link',
			'action_abuse_link',
			'web_ui',
		)
		template_args = {k: 'Placeholder' for k in template_keys}
		for template_name in tenca.templates.templates_dict:
			self.assertEqual(
				tenca.templates.substitute(template_name, **template_args),
				self.read(tenca.templates.http_substitute_url(template_name, **template_args))
			)
