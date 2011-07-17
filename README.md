# ParašykJiems

## Development setup

The system is developed and tested on GNU/Linux with Python 2.7. The
required Python packages are

 - Django 1.3
 - pysqlite
 - django-debug-toolbar

After cloning the repository, execute the following commands to
initialize the database:

    python manage.py syncdb
    python manage.py compilemessages
    python manage.py importMembers
    python manage.py importTerritories

The site's data is stored in text files in the repository itself and
the last two commands import that data.

To launch the development server, execute

    python manage.py runserver


## Data update authentication

Before using any pages in /data/update the user should authenticate in
/admin. User accounts are standard Django user accounts.
