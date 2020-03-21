#!/usr/bin/env python
#  api/look/app_flask.py

from flask import Flask
import json
import os
import sys

local_base_dir = '../../url_www'
local_base_url = '/url_www'

script_dir = os.path.dirname(__file__)

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]


api = Flask(__name__, static_url_path='', static_folder=local_base_dir)

@api.route('/companies', methods=['GET'])
def get_companies():
  return json.dumps(companies)

@api.route(local_base_url + '/<path:path>', methods=['GET'])
def get_url_www(path):
  base_dir_pth = os.path.abspath( script_dir + '/' + local_base_dir)
  thisdir = os.getcwd()
  req_pth = os.path.abspath(thisdir + local_base_url + '/' + path)
  if not req_pth.startswith(base_dir_pth):
      return "Error: requested content not in the directory tree"
  return api.send_static_file(path)

if __name__ == '__main__':
    api.run()

