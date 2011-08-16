# ParašykJiems

## Development setup

The system is developed and tested on GNU/Linux with Python 2.7. The
required Python packages are

 - Django 1.3
 - pysqlite or some other database
 - django-haystack
 - South
 - unidecode (used for transliteration in search)
 - progressbar — for importdata and tidy_locations commands
 - gunicorn — for launching a production server

After cloning the repository, execute the following commands to
initialize the installation:

    python manage.py syncdb
    python manage.py compilemessages

Export data from production and put the CSV files into the 'data'
folder, then run:

    python manage.py importdata
    python manage.py tidy_elderates
    python manage.py update_locations
    python manage.py generate_slugs
    python manage.py rebuild_index

To launch the development server on localhost:8000, execute

    python manage.py runserver


## Mail setup

There is a 'process_message' command, which takes an email message from
stdin and processes it as if it was a response to an enquiry.

To deliver mail to our system with Postfix and Maildrop, create an
alias which delivers all messages with parts like reply+123 to some
user, for example parasykjiems. Add

    reply: parasykjiems

to /etc/postfix/aliases, run newaliases and set recipient_delimiter to
+ in /etc/postfix/main.cf. Then in the parasykjiems user's home
directory create a .forward file which contains

    "|/usr/bin/maildrop"

Then copy the mailfilter.example file from the repository to
~/.mailfilter and edit it in accordance to your configuration. The
file should be chmodded to 600. Specifically, set the PARASYKJIEMS
variable to the repository path.

Should a message's delivery fail, it will be put into the
reply_fail.mbox file.

Some other aliases that should be defined are 'abuse' and 'feedback'.
