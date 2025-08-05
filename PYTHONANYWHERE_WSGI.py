# +++++++++++ PYTHON ANYWHERE WSGI CONFIGURATION +++++++++++
# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys

# Add your project path here
project_home = '/home/yourusername/jmcomic-downloader'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Add JMComic to path
jmcomic_path = '/home/yourusername/jmcomic-downloader/JMComic-Crawler-Python-master/src'
if jmcomic_path not in sys.path:
    sys.path.insert(0, jmcomic_path)

# Import your application
from app import application

# This is the WSGI callable that PythonAnywhere will use
# to serve your application
if __name__ == '__main__':
    # This is just for testing locally
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8000, application)
    httpd.serve_forever()