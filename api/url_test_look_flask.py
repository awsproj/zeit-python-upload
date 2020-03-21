#!/usr/bin/env python
#   api/look/url_test.py

import sys
#if sys.hexversion < 0x03050000:
#    sys.exit("Python 3.5 or newer is required to run this program.")

import os

from look.app_flask import api

if __name__ == '__main__':
    api.run()

# note: tested on windows 10 python 2.7.14 and Jinja2-2.11.1 MarkupSafe-1.1.1 
#       Werkzeug-1.0.0 click-7.1.1 flask-1.1.1 itsdangerous-1.1.0


