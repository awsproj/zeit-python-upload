#!/usr/bin/env python
# /api/index.py
# https://zeit.co/docs/runtimes#official-runtimes/python/python-version

from http.server import BaseHTTPRequestHandler
from cowpy import cow
from urllib.parse import urlparse

class handler(BaseHTTPRequestHandler):

    c_handler_source = 'None'

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        call_source = 'None'
        if type(handler.c_handler_source) is not type(None):
            if type(handler.c_handler_source) is str:
                call_source = 'type str ' + str(handler.c_handler_source)
            elif type(handler.c_handler_source) is unicode:
                call_source = 'type ucd ' + str(handler.c_handler_source)
            else:
                call_source = 'type else ' + str(type(handler.c_handler_source))
                call_source += ' ' + str(handler.c_handler_source)

        urlpth, urlobj, urlqry = 'a', 'b', 'c'
        try:
            urlpth = self.path
            urlobj = urlparse(urlpth)
            urlqry = urlobj.query
        except:
            pass
        message = cow.Cowacter().milk('Hello from Python from a ZEIT Now Serverless Function!'\
                                      + ' ' + call_source + ' ' + urlpth + ' ' + urlqry)
        self.wfile.write(message.encode())
        return

if __name__ == '__main__':
    import sys
    sys.stderr.write("running in main ...\n")
    handler.c_handler_source = '__Main__'
    from http.server import HTTPServer
    server = HTTPServer(("", 8000), handler)
    sys.stderr.write("running on port 8000 ...\n")
    server.serve_forever()

