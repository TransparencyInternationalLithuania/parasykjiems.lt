LOCAL_SETTINGS_VERSION = 13


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

# Feedback is sent here.
FEEDBACK_EMAIL = 'feedback@' + SITE_DOMAIN

# Used as From adress for emails sent by the service, except enquiries.
SERVER_EMAIL = 'parasykjiems@' + SITE_DOMAIN

# Reply emails are formatted like
# {REPLY_EMAIL_PREFIX}+{id}.{secret}@{SITE_DOMAIN}
REPLY_EMAIL_PREFIX = 'reply'

# Additional content to put into every page's head tag. Useful for
# Google Analytics script tags.
ADDITIONAL_HTML_HEAD = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ww7h#q+rru)mz=$e=gbyb(6n7cm0eb2!2bh+y5ahad)4iq-1vg'


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

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'parasykjiems',
    },
}
