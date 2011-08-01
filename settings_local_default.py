DEBUG = True

ADMINS = (
    ('Local', 'parasykjiems@localhost'),
)

# Print emails to console.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SERVER_EMAIL = 'parasykjiems@localhost'

# Should contain {unique_hash} somewhere.
ENQUIRY_EMAIL_FORMAT = 'parasykjiems+{unique_hash}@localhost'

# This email receives user feedback messages.
FEEDBACK_EMAIL = 'parasykjiems@localhost'

# Used for absolute URLs. Shouldn't include trailing slash, but should
# include URL scheme.
SITE_ADDRESS = 'http://localhost:8000'

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
