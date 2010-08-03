


1. Installation instructions.


Pre-requisites:

1. prepare python to work with Google Docs API
Read all instructions here: googledocs for python: http://code.google.com/apis/gdata/articles/python_client_lib.html

Short version:
Try importing the ElementTree module. If you are using Python 2.5 or higher, enter the following in the interpreter:
from xml.etree import ElementTree
If the import fails, then install ElementTree (http://pypi.python.org/pypi/elementtree/)

Installing the Google Data Library:
http://code.google.com/p/gdata-python-client/downloads/list

# install enum library
pip install enum
2. Solr and django-haystack (http://haystacksearch.org/) are required. Solr also requires pysolr library.
If you prefer not Solr, but some other search engine, read here: http://docs.haystacksearch.org/dev/installing_search_engines.html


2. Available commands

# prints a list of first 5 Lithuanian countries. 
manage.py printCounties 5 

# runs all tests
manage.py test 

# runs only tests for contactdb app
manage.py test contactdb

# runs an embedded web server
manage.py runserver

# cleans all database from contact data
manage.py clearcontactDB


3. After installation

# creates database
manage.py syncdb

# downloads data from google docs to be ready for import:
manage.py downloadDocs

# imports all database with contact data
manage.py importcontactDB




