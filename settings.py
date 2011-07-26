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

SITE_ID = 1

USE_I18N = True
USE_L10N = True

MEDIA_ROOT = ''
MEDIA_URL = ''

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ww7h#q+rru)mz=$e=gbyb(6n7cm0eb2!2bh+y5ahad)4iq-1vg'

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
    "django.contrib.messages.context_processors.messages",
    "parasykjiems.web.menu.context_processor",
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'parasykjiems.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'parasykjiems.web',
    'haystack',
)

HAYSTACK_SITECONF = 'parasykjiems.search_sites'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


if os.path.exists('settings_local.py'):
    from settings_local import *
else:
    from shutil import copy
    print 'Initializing local settings.'
    copy('settings_local_default.py', 'settings_local.py')


MANAGERS = ADMINS
TEMPLATE_DEBUG = DEBUG


# Use an SQLite database for testing to avoid having to grant
# privileges when using PostgreSQL. Also, database
# creation/destruction is faster this way.
#
# The actual implementation of this is a bit hacky.
if sys.argv[1] == 'test':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test',
    }
