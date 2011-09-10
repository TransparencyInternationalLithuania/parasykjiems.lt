LOCAL_SETTINGS_VERSION = 6


DEBUG = True

ADMINS = (
    ('Local', 'parasykjiems@localhost'),
)

MANAGERS = ADMINS


# Show a warning on top of every page that this is a development version.
TESTING_VERSION = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# If this is the testing version, redirect all enquiries to this
# address.
REDIRECT_ENQUIRIES_TO = 'feedback@localhost'

MAIL_DOMAIN = 'localhost'

# Feedback is sent here
FEEDBACK_EMAIL = 'feedback@' + MAIL_DOMAIN

# Various email addresses used by the system:
SERVER_EMAIL = 'parasykjiems@' + MAIL_DOMAIN
ABUSE_EMAIL = 'abuse@' + MAIL_DOMAIN

# Should contain {id} and {hash} somewhere, which will be replaced by
# numbers.
ENQUIRY_EMAIL_FORMAT = 'reply+{id}.{hash}@' + MAIL_DOMAIN

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
