LOCAL_SETTINGS_VERSION = 4


DEBUG = True

ADMINS = (
    ('Local', 'parasykjiems@localhost'),
)

MANAGERS = ADMINS


# Show a warning on top of every page that this is a development version.
TESTING_VERSION = True

# If this is the testing version, redirect all enquiries to this
# address.
REDIRECT_ENQUIRIES_TO = 'representative@localhost'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

MAIL_DOMAIN = 'localhost'
def email(user):
    return '{}@{}'.format(user, MAIL_DOMAIN)

# Various email addresses used by the system:
SERVER_EMAIL = email('parasykjiems')
FEEDBACK_EMAIL = email('feedback')
ABUSE_EMAIL = email('abuse')

# Should contain {reply_hash} somewhere.
ENQUIRY_EMAIL_FORMAT = email('reply+{reply_hash}')

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
