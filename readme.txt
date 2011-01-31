


1. Installation instructions.


Pre-requisites:

1. prepare python to work with Google Docs API
Read all instructions here: googledocs for python: http://code.google.com/apis/gdata/articles/python_client_lib.html

Short version:
Try importing the ElementTree module. If you are using Python 2.5 or higher, enter the following in the interpreter:
from xml.etree import ElementTree
If the import fails, then install ElementTree (http://pypi.python.org/pypi/elementtree/)

Installing the Google Data Library:
http://code.google.com/apis/documents/code.html
http://code.google.com/apis/documents/docs/3.0/developers_guide_python.html


# Solr and django-haystack (http://haystacksearch.org/) are required. Solr also requires pysolr library.
If you prefer not Solr, but some other search engine, read here: http://docs.haystacksearch.org/dev/installing_search_engines.html


2. Available commands
# runs all tests
manage.py test 

# runs an embedded web server
manage.py runserver

# cleans all database from contact data. This does not clean data enetered by users
manage.py clearAll



3. Creating a database with mysql
Connect as root
	mysql -u root

and create database with utf8 character set:
	create database writetothem character set utf8;

issue manage.py syncdb to populate database with tables

4. After installation

# creates database
manage.py syncdb

# download lithuanian data from google docs 
manage.py ltGeoDataDownloadDocs

# downloads data from google docs to be ready for import:
manage.py downloadDocs

# imports initial data, such as data, which changes only every years
manage.py importInitial

# imports other data, which can be updated quite often (even daily)
manage.py importAll

# update source code on server. First command will download updates from bitbucket (but wont change anything). Second will update to newest changeset and will discard any uncomitted changes
sudo hg pull
sudo hg update --clean

#runing server with nginx and gunicorn. Do not run python with super user 
python manage.py run_gunicorn 127.0.0.1:1234 --daemon
# use this to run server with user parasykjiems
sudo -u parasykjiems python manage.py run_gunicorn 127.0.0.1:1234 --daemon

# to kill a running gunicorn instance
ps ax | grep manage.py
sudo kill (process number)

# after running thse four commands you should have your database ready. just call manage.py runserver and use browser :)

5. Help and bug fixes
If you have any problems setting up the project, or get unexpected exsceptions, dont hesistate to report everything at http://bitbucket.org/dariusdamalakas/parasykjiems

This project is part of http://manovalstybe.lt/ initiative




Linux for newbies:
To create an admin group and add it to sudoers

visudo
%admin ALL=(ALL) ALL

groupadd admin


Create a new user and add user to group admin
useradd username
passwd username
mkdir /home/username
chown username:users /home/username/
usermod -a -G admin username




When server is installed, add these cronjobs to special dedicated user (for example, wtt)


MAILTO=wtterrors@gmail.com
45 * * * * /var/www/beta.parasykjiems.lt/scripts/updateDaily.sh
5,15,25,35,45,55 * * * * /var/www/beta.parasykjiems.lt/scripts/getResponses.sh

