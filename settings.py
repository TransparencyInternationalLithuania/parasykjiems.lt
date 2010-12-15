# Django settings for parasykjiems project.
from GlobalSettingsClass import GlobalSettingsClass, GlobalSettingsMail

SERVER_EMAIL = 'parasykjiems@gmail.com'

ADMINS = (
    ('Error Group', 'parasykjiems-errors@googlegroups.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'lt-LT'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '5m-$e-&(uu8g#ud#vat^55iyfbh+%ujs=8#4*6-*z6f_+xqla*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'parasykjiems.urls'

#HAYSTACK_INCLUDE_SPELLING = True

def prepareSettingsLocal():
    import os
    import shutil
    if (os.path.exists("settings_local.py") == False):
        print "settings_local.py does not exist"
        print "creating new settings from settings_local.py.template"
        shutil.copy("settings_local.py.template", "settings_local.py")
    

GlobalSettings = GlobalSettingsClass()
GlobalSettings.mail = GlobalSettingsMail();

prepareSettingsLocal()
from settings_local import *

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.formtools',
#    'chronograph',
#    'parasykjiems.polls',
    'parasykjiems.contactdb',
    'parasykjiems.pjweb',
    'parasykjiems.pjutils',
    'django.contrib.admin',
    #'gunicorn',
#    'haystack',
    'cdb_lt_civilparish',
    'cdb_lt_mps',
    'cdb_lt_municipality',
    'cdb_lt_seniunaitija',
    'cdb_lt_streets') + GlobalSettings.LiveServerApps 
    #'haystack')


# send feedback from website to this email address
GlobalSettings.mail.feedbackEmail = "parasykjiems@gmail.com"