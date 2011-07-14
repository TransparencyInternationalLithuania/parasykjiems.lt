# ParašykJiems

## Installation

Requirements:

 - Python 2.7
 - Django 1.3

The system is developed and tested on a GNU/Linux system.

After cloning the repository, execute the following commands to
initialize the database:

    python manage.py syncdb
    python manage.py importMembers
    python manage.py importTerritories

The site's data is stored in text files in the repository itself and
the last two commands import that data.

To launch the development server, execute

    python manage.py runserver
