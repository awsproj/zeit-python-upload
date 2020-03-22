#!/usr/bin/env python
#  api/look/app_flask.py

from flask import Flask, request
import json
import os
import sys

local_base_dir = '../../url_www'
local_base_url = '/url_www'

script_dir = os.path.dirname(__file__)

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]


api = Flask(__name__, static_url_path='/url_www', static_folder=local_base_dir)

@api.route('/api/<path:ver_str>', methods=['GET'])
def get_api_v0xy(ver_str): # http://<ip>:<port>/api/v001?abcd=1234
  the_ver = ver_str # v001
  the_req = request
  the_path = the_req.path # /api/v001
  the_query = the_req.query_string # abcd=1234
  return json.dumps(companies)

@api.route(local_base_url + '/<path:path>', methods=['GET'])
def get_url_www(path):
  base_dir_pth = os.path.abspath( script_dir + '/' + local_base_dir)
  thisdir = os.getcwd()
  req_pth = os.path.abspath(thisdir + local_base_url + '/' + path)
  if not req_pth.startswith(base_dir_pth):
      return "Error: requested content not in the directory tree"
  return api.send_static_file(path)

@api.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    https://stackoverflow.com/questions/34066804/disabling-caching-in-flask
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    api.run()

