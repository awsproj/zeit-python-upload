#!/usr/bin/env python
#  api/look/app_falcon.py

# install falcon 2.0.0

import falcon, json


# code from the falcon tutorial
#app = application = falcon.API()


# code below from https://stoplight.io/blog/python-rest-api/
class CompaniesResource(object):
  companies = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]
  def on_get(self, req, resp):
    resp.body = json.dumps(self.companies)

api = falcon.API()
companies_endpoint = CompaniesResource()
api.add_route('/companies', companies_endpoint)

# run gunicorn falconapi:api
# refer to for debugging in pycharm:
#   https://stackoverflow.com/questions/47464315/environment-set-up-for-running-a-falcon-app

