# ParašykJiems

## Development setup

The system is developed and tested on GNU/Linux with Python 2.7. The required
Python packages are listed in requirements*.txt, you can install all Python
requirements using this command:

    pip install -r requirements.txt -r requirements-dev.txt

After cloning the repository, execute the following commands to initialize the
installation:

    python manage.py compilemessages
    python manage.py syncdb
    python manage.py migrate

Export data from production and put the CSV files into the `data` folder, then
run:

    python manage.py import_articles
    python manage.py import_snippets
    python manage.py import_search
    python manage.py update_locations
    python manage.py generate_slugs
    python manage.py rebuild_index

The last few commands may take a while. To launch the development server on
localhost:8000, execute

    python manage.py runserver


## Local settings

The file `local_settings_default.py` should be copied to
`local_settings.py` and modified appropriately. A value suitable for the
`SECRET_KEY` option can be generated by executing the following expression in
the Python interpreter:

    import os
    os.urandom(40)


## Mail setup

There is a `process_message` command, which takes an email message from stdin
and processes it as if it was a response to an enquiry.

To deliver mail to our system with Postfix and Maildrop, create an alias which
delivers all messages with parts like reply+123 to some user, for example
parasykjiems. Add

    reply: parasykjiems

to `/etc/postfix/aliases`, run newaliases and set `recipient_delimiter` to
`+` in `/etc/postfix/main.cf`. Then in the parasykjiems user's home directory
create a `.forward` file which contains

    "|/usr/bin/maildrop"

Then copy the `mailfilter.example` file from the repository to `~/.mailfilter` and
edit it in accordance to your configuration. The file should be chmodded to
600. Specifically, set the PARASYKJIEMS variable to the repository path.

Should a message's delivery fail, it will be put into the `reply_fail.mbox` file.
