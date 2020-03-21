#!/usr/bin/env python
#  url_test_coms_tee.py 


import os, sys

tendo_dir = "python_pkg_tendo/tendo_master"
if os.path.isdir(tendo_dir):
    sys.path.insert(0, tendo_dir)
else:
    raise Exception("No tendo_dir as a dir")


import tendo.tee as tee


# tee stdout to a file
tee.system("\\Python\\python.exe url_test_coms.py", logger="url_test_log_file.txt", stdout=sys.stdout)


