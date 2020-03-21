#!/usr/bin/env python
#   url_test_paths.py

import sys
if sys.hexversion < 0x03050000:
    sys.exit("Python 3.5 or newer is required to run this program.")

from http.server import SimpleHTTPRequestHandler as BaseHandler
import os

class HTTPHandler(BaseHandler):
    def translate_path(self, path):
        do_path_mod = False
        mod_path_len = 0
        mod_start = ''
        try:
            mod_path_len = len(self.server.url_base_path)
            mod_start = self.server.url_base_path
            do_path_mod = True
        except:
            pass
        if do_path_mod:
            if len(path) < mod_path_len:
                return None
            if path.startswith(mod_start):
                path = path[mod_path_len:]
                if path == '':
                    path = '/'
        path = BaseHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.local_base_path, relpath)
        return fullpath

