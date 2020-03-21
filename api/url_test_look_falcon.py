#!/usr/bin/env python
#   api/look/url_test.py

import sys
#if sys.hexversion < 0x03050000:
#    sys.exit("Python 3.5 or newer is required to run this program.")

if (sys.version_info < (3, 0)):
    from BaseHTTPServer import BaseHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    from urlparse import urlparse
    ver = 2
else:
    from http.server import BaseHTTPRequestHandler
    from http.server import HTTPServer
    from cowpy import cow
    from urllib import parse as urlparse
    ver = 3

import os

from look.app_falcon import api

port = 8000
local_base_path = ""
url_base_path = ""


class urlTestServer(HTTPServer): # not invoked on zeit server-less
    def __init__(self, local_path, url_path, server_address,
                                            RequestHandlerClass=api):
        self.local_base_path = local_path  # d:\\zeit_proj\\src\\url_www
        self.url_base_path = url_path      # url_www
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == '__main__':
    # translate 'storage' in url to local 'url_www'
    prog_dir = os.path.dirname(__file__)
    topdir = os.path.abspath(prog_dir + "/../")
    www_dir = os.path.join(topdir, local_base_path)
    server = urlTestServer(www_dir, url_base_path, ("", port))

    print('Started httpserver on port %d' % port)

    #Wait forever for incoming http requests
    server.serve_forever()

# note: this is tested on a windows 10 python 2.7.14 with falcon 2.0.0. 
#       a few errors are raised. 


