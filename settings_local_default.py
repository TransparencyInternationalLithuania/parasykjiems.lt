LOCAL_SETTINGS_VERSION = 9


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

SITE_DOMAIN = 'localhost'

# Like SITE_DOMAIN, but may include the HTTP port if it's not 80.
SITE_HOST = SITE_DOMAIN + ':8000'

# Used for absolute URLs. Shouldn't include trailing slash, but should
# include URL scheme.
SITE_ADDRESS = 'http://' + SITE_HOST

# Feedback is sent here
FEEDBACK_EMAIL = 'feedback@' + SITE_DOMAIN

# Various email addresses used by the system:
SERVER_EMAIL = 'parasykjiems@' + SITE_DOMAIN
ABUSE_EMAIL = 'abuse@' + SITE_DOMAIN

# Should contain {id} and {hash} somewhere, which will be replaced by
# numbers.
ENQUIRY_EMAIL_FORMAT = 'reply+{id}.{hash}@' + SITE_DOMAIN

# Additional content to put into every page's head tag. Useful for
# Google Analytics script tags.
ADDITIONAL_HTML_HEAD = ''

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
