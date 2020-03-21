#!/usr/bin/env python
#  api/look/app_flask.py
#  code from https://stoplight.io/blog/python-rest-api/

from flask import Flask
import json

companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

api = Flask(__name__)

@api.route('/companies', methods=['GET'])
def get_companies():
  return json.dumps(companies)

if __name__ == '__main__':
    api.run()

