# Django settings for parasykjiems project.
from GlobalSettingsClass import GlobalSettingsClass, GlobalSettingsMail, GlobalSettingsIMAP, GlobalSettingsSMTP
from pjweb.email.backends import EmailInfoInToField, EmailInfoInSubject

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

ROOT_URLCONF = 'urls'


commonApps = ['django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.formtools',
#    'chronograph',
#    'parasykjiems.polls',
    'contactdb',
    'pjweb',
    'pjutils',
    'django.contrib.admin',
    #'gunicorn',
#    'haystack',
    'cdb_lt_civilparish',
    'cdb_lt_mps',
    'cdb_lt_municipality',
    'cdb_lt_seniunaitija',
    'cdb_lt_streets']

#HAYSTACK_INCLUDE_SPELLING = True

def applyDefaultSettings():
    GlobalSettings.mail = GlobalSettingsMail();
    # send feedback from website to this email address
    GlobalSettings.mail.feedbackEmail = "parasykjiems@gmail.com"

    # IMAP settings
    GlobalSettings.mail.IMAP = GlobalSettingsIMAP()

    # this is used to build a reply to address when sending emails
    GlobalSettings.mail.IMAP.EMAIL_PUBLIC_HOST = 'dev.parasykjiems.lt'
    GlobalSettings.mail.IMAP.EMAIL_HOST_TYPE = 'IMAP'
    GlobalSettings.mail.IMAP.EMAIL_HOST = 'dev.parasykjiems.lt'
    GlobalSettings.mail.IMAP.EMAIL_PORT = '5143'
    GlobalSettings.mail.IMAP.EMAIL_HOST_USER = 'vytautas'
    GlobalSettings.mail.IMAP.EMAIL_HOST_PASSWORD = 'devdev'



    # SMTP settings
    GlobalSettings.mail.SMTP = GlobalSettingsSMTP()
    GlobalSettings.mail.SMTP.EMAIL_HOST = ''
    GlobalSettings.mail.SMTP.EMAIL_PORT = 25
    GlobalSettings.mail.SMTP.EMAIL_HOST_USER = ""
    GlobalSettings.mail.SMTP.EMAIL_HOST_PASSWORD = ""
    GlobalSettings.mail.SMTP.EMAIL_USE_TLS = False


    # this controls where a info about which emails relates to which message in database is put.
    # At the moment there are plans to support three backends:
    # EmailInfoInToField - stores information in to field. So when representative gets an email,
    #     a reply-to field will be semething like 'somepreifx_%s_%s@yourdomain' % (mail.id, mail.hash)
    # EmailInfoInSubject - stores information in subject field. This allows us to use this backend with gmail boxes
    #     where an IMAP server does not have to support catch-all (i.e. all messages go to single mail box)
    # EmailInfoDogsAndCats - instead of saving message id in one of the field, a reply-to address is a combination
    #     of random words, where is smaller than 3 letters. This will circumvent (probably) spam filters reliably.
    emailInfoInToField = EmailInfoInToField()
    emailInfoInToField.Email_public_host = GlobalSettings.mail.IMAP.EMAIL_PUBLIC_HOST

    emailInfoInSubject = EmailInfoInSubject()
    EmailInfoInSubject.DefaultReplyTo = GlobalSettings.mail.IMAP.EMAIL_HOST_USER

    GlobalSettings.mail.composition_backends = [emailInfoInToField, emailInfoInSubject]



# Create settings_local.py file from template, if does not exist
def prepareSettingsLocal():
    import os
    import shutil
    if os.path.exists("settings_local.py") == False:
        print "settings_local.py does not exist"
        print "creating new settings from settings_local.py.template"
        shutil.copy("settings_local.py.template", "settings_local.py")

# Create GlobalSetttings class to store app specific settings (compared to Django specific)

GlobalSettings = GlobalSettingsClass()
applyDefaultSettings()

# load settings_local file.
prepareSettingsLocal()
from settings_local import *

INSTALLED_APPS = tuple(commonApps + GlobalSettings.LiveServerApps)
# no settings should be below this line. Add standard settings to applyDefaultSettings
# or write them in settings_local file, if they are specific for your deployment

# copy to DJANGO smtp variables our own settings
# You should never use Django SMTP variables. Instead use
# settings from GlobalSettings.mail.SMTP object
# Define values for these settings in settings_local.py file
EMAIL_HOST = GlobalSettings.mail.SMTP.EMAIL_HOST
EMAIL_PORT = GlobalSettings.mail.SMTP.EMAIL_PORT
EMAIL_HOST_USER = GlobalSettings.mail.SMTP.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = GlobalSettings.mail.SMTP.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = GlobalSettings.mail.SMTP.EMAIL_USE_TLS
