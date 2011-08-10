DEBUG = True

ADMINS = (
    ('Local', 'parasykjiems@localhost'),
)

MANAGERS = ADMINS


# Redirect all enquiries to this address. Useful for testing.
REDIRECT_ENQUIRIES = True
REDIRECT_ENQUIRIES_EMAIL = 'representative@localhost'


# Print emails to console.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SERVER_EMAIL = 'parasykjiems@localhost'

# Send all enquiries and confirmation requests to this address if
# DEBUG is True.
DEBUG_EMAIL_RECIPIENT = 'parasykjiems@localhost'

# Should contain {reply_hash} somewhere.
ENQUIRY_EMAIL_FORMAT = 'reply+{reply_hash}@localhost'

# This email receives user feedback messages.
FEEDBACK_EMAIL = 'feedback@localhost'

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
