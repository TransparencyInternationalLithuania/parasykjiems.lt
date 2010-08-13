


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


# Solr and django-haystack (http://haystacksearch.org/) are required. Solr also requires pysolr library.
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

3. Creating a database with mysql
Connect as root
	mysql -u root

and create database with utf8 character set:
	create database writetothem character set utf8;

issue manage.py syncdb to populate database with tables

4. After installation

# creates database
manage.py syncdb

# downloads data from google docs to be ready for import:
manage.py downloadDocs

# imports initial data, such as data, which changes only every years
manage.py importInitial

# imports other data, which can be updated quite often (even daily)
manage.py importAll

5. Help and bug fixes
If you have any problems setting up the project, or get unexpected exsceptions, dont hesistate to report everything at http://bitbucket.org/dariusdamalakas/parasykjiems

This project is part of http://manovalstybe.lt/ initiative