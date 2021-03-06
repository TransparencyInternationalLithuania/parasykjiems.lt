import os
import sys


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))


def project_relative(path):
    return os.path.join(PROJECT_ROOT, path)

DEBUG = True

ADMINS = ()


TIME_ZONE = 'Europe/Vilnius'

_ = lambda x: x

LANGUAGE_CODE = 'lt'
LANGUAGES = (
    ('en', _('English')),
    ('lt', _('Lithuanian')),
)

LOCALE_PATHS = (
    project_relative('locale'),
)

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = project_relative('media/')
MEDIA_URL = '/media/'

STATIC_ROOT = ''
STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    project_relative('static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_DIRS = (
    project_relative('templates'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",

    "parasykjiems.web.context_processors.expose_settings",
)

MIDDLEWARE_CLASSES = (
    'parasykjiems.middleware.SetRemoteAddrMiddleware',
    'parasykjiems.middleware.SetHostBehindProxyMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ('127.0.0.1',)

APPEND_SLASH = False
USE_ETAGS = True

ROOT_URLCONF = 'parasykjiems.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    'haystack',
    'south',
    'cachebuster',
    'debug_toolbar',

    'web',
    'search',
    'mail',
    'scrape',
)

if not os.path.exists(project_relative('settings_local.py')):
    from shutil import copy
    print 'Initializing local settings.'
    copy(project_relative('settings_local_default.py'), project_relative('settings_local.py'))

from settings_local import *

from settings_local_default import \
     LOCAL_SETTINGS_VERSION as SETTINGS_VERSION
if LOCAL_SETTINGS_VERSION < SETTINGS_VERSION:
    raise Exception(
        'Local settings are version {} but should be updated to {}.'.format(
            LOCAL_SETTINGS_VERSION,
            SETTINGS_VERSION))

TEMPLATE_DEBUG = DEBUG


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
        'search': {
            'format': '%(asctime)s %(message)s'
        },
    },
    'handlers': {
        'debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filename': project_relative('logs/debug.log'),
            'maxBytes': 1024 * 1024 * 5,
        },
        'info': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'verbose',
            'filename': project_relative('logs/info.log'),
            'backupCount': 5,
            'maxBytes': 1024 * 1024 * 5,
        },
        'warning': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'verbose',
            'filename': project_relative('logs/warning.log'),
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'search': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'search',
            'filename': project_relative('logs/search.log'),
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['warning', 'info', 'debug'],
        },
        'search': {
            'level': 'INFO',
            'handlers': ['search'],
        },
        'pysolr': {
            'level': 'DEBUG',
            'handlers': ['null'],
            'propagate': False,
        },
    },
}


# Use an SQLite database for testing to avoid having to grant
# privileges when using PostgreSQL. Also, database
# creation/destruction is faster this way.
#
# The actual implementation of this is a bit hacky.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
    }

# Allow usage of 'static' templatetag without explicitly loading cachebuster.
from django.template.loader import add_to_builtins
add_to_builtins('cachebuster.templatetags.cachebuster')

