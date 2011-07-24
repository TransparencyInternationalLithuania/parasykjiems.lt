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
    python manage.py update_index

To launch the development server on localhost:8000, execute

    python manage.py runserver
