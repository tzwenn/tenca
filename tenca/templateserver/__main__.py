from . import application

import argparse
import wsgiref.simple_server


default_host = 'localhost'
default_port = 8080

parser = argparse.ArgumentParser(
	prog="python -m tenca.templateserver", 
	description='Run the tenca template server'
)
parser.add_argument('-b', '--bind', metavar='ADDRESS', default=default_host,
		help='The address to bind to (default: {})'.format(default_host))
parser.add_argument('port', metavar='PORT', type=int, default=default_port,
		help='The port to listen on (default: {})'.format(default_port))
args = parser.parse_args()


with wsgiref.simple_server.make_server(args.bind, args.port, application) as server:
	print("Serving on http://{}:{}".format(args.bind, args.port))
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		pass