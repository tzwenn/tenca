from ..templates import templates_dict

from abc import ABCMeta, abstractmethod
import http
import string
import urllib.parse


class WebApp(object, metaclass=ABCMeta):

	"""Callable WSGI-compatible object, without external dependencies.
	Can be served with wsgiref/flup/gunicorn.
	"""

	CONTENT_TYPE = 'text/plain; charset=utf-8'

	def __init__(self):
		pass

	def __call__(self, environ, start_response):
		path = environ.get('PATH_INFO', '/')
		query = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
		self.environ = environ
		self._content = []
		status = self.run(path, query)
		response = '{} {} '.format(status.value, status.name)
		start_response(response, [('Content-Type', self.CONTENT_TYPE)])
		return self._content

	def write(self, text):
		self._content.append(text.encode('utf-8'))

	@abstractmethod
	def run(self, path, params):
		"""Re-implement in subclass:
		
		Handle HTTP GET on `path` with `query`"""


class TemplateServerApp(WebApp):

	"""WSGI-compatible object that formats tenca.templates from HTTP requests.
	
	Upon module-load, all members of the tenca.templates module are iterated and
	subclasses of string.Template served under '/attribute_name'.
	The template placeholders are filled from HTTP GET parameters.

	Uses HTTP status codes for replies, i.e. HTTP 200 and plain-text content
	if successfull, HTTP 404 if non-existend template is requested, or
	HTTP 400  if any template argument is missing from the GET query.
	"""

	def flatten_query(self, query):
		return {key: value[0] for key, value in query.items()}

	def run(self, path, query):
		try:
			template = templates_dict[path.rstrip('/').rsplit('/', 1)[-1]]
		except KeyError:
			return http.HTTPStatus.NOT_FOUND
		try:
			content = template.substitute(**self.flatten_query(query))
		except KeyError:
			return http.HTTPStatus.BAD_REQUEST
		self.write(content)
		return http.HTTPStatus.OK


application = TemplateServerApp()
