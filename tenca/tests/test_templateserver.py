import tenca.settings
import tenca.templates
import tenca.templateserver

import http
import unittest
import urllib.error
import urllib.parse
import urllib.request

class TemplateRequestTest(unittest.TestCase):
	"""Access via HTTP as given in `settings.TEMPLATE_SERVER_ADDRESS`"""

	def url(self, path):
		return '{}/{}'.format(tenca.settings.TEMPLATE_SERVER_ADDRESS, path)

	def open(self, path, **kwargs):
		fragments = urllib.parse.urlencode(kwargs)
		if fragments:
			fragments = '?' + fragments
		urllib.request.urlopen(self.url(path) + fragments)

	def read(self, url):
		return urllib.request.urlopen(url).read().decode('utf-8')

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
			self.open('mail_footer', **kwargs)
		try:
			self.open('mail_footer', **kwargs)
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

class TemplateAppTest(TemplateRequestTest):
	"""Access the WSGI-object"""

	def setUp(self):
		self.app = tenca.templateserver.TemplateServerApp()

	def _start_response(self, status, headers):
		self._code = int(status.split(maxsplit=1)[0])
		self._headers = headers

	def call(self, environ):
		response = b''.join(self.app(environ, self._start_response))
		if self._code != http.HTTPStatus.OK:
			raise urllib.error.HTTPError(environ['PATH_INFO'], self._code, response, self._headers, None)
		return response

	def open(self, path, **kwargs):
		self.call(dict(
			PATH_INFO=path,
			QUERY_STRING=urllib.parse.urlencode(kwargs)
		))

	def read(self, url):
		splits = urllib.parse.urlsplit(url)
		return self.call(dict(
			PATH_INFO=splits.path,
			QUERY_STRING=splits.query
		)).decode('utf-8')