DEBUG = True


ADMINS = (
    ('Local', 'parasykjiems@localhost'),
)


# This email receives user feedback messages.
FEEDBACK_EMAIL = 'parasykjiems@localhost'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'parasykjiems.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = 'parasykjiems.index'
