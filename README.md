# ParašykJiems

## Development setup

The system is developed and tested on GNU/Linux with Python 2.7. The
required Python packages are

 - Django 1.3
 - pysqlite or some other database
 - django-haystack
 - unidecode — used for transliteration in search
 - progressbar — only for data migration from older version

After cloning the repository, execute the following commands to
initialize the database:

    python manage.py syncdb
    python manage.py compilemessages

Export data from production and put the CSV files into the 'data'
folder, then run:

    python manage.py importdata
    python manage.py update_locations
    python manage.py update_index

To launch the development server on localhost:8000, execute

    python manage.py runserver


## Mail setup

There is a 'process_mail' command, which takes an email message from
stdin and processes it as if it was a response to an enquiry.

Our system is tested with Postfix, but other mail systems which can
pipe messages to other processes could theoretically be used. To setup
Postfix to deliver messages to parasykjiems, main.cf should contain

    transport_maps = regexp:/etc/postfix/transport

/etc/postfix/transport should contain

    /^parasykjiems+.*@/ parasykjiems:

And master.cf should contain something like

    parasykjiems unix - n n - - pipe
      user=parasykjiems:parasykjiems
      directory=/home/parasykjiems/parasykjiems
      argv=../bin/python manage.py process_mail

Adjust directories and user names in accordance to your system.
