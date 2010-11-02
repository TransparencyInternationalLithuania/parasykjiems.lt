from django.conf.urls.defaults import *

#from parasykjiems.pjweb.views import ContactForm
#from django import forms

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('parasykjiems.pjweb.views',
    # Example:
    # (r'^parasykjiems/', include('parasykjiems.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Handle start page
    (r'^$', 'index'),
    (r'^contact/(\w+)/(\d+)/no_email/$', 'no_email'),
    (r'^contact/(\w+)/(\w+)/(\w+)/smtp_error/$', 'smtp_error'),

    #(r'^choose_rep/(\w+)/(\w+)/(\w+)/(\d+)$', 'choose_representative'),
    (r'^choose_rep/([a-zA-Z0-9_ ]+)/([a-zA-Z0-9_ ]+)/([a-zA-Z0-9_ ]+)/$', 'choose_representative'),
    (r'^choose_rep/([a-zA-Z0-9_ ]+)/([a-zA-Z0-9_ ]+)/([a-zA-Z0-9_ ]+)/(\d+)/$', 'choose_representative'),
    #(r'^choose_rep/(\w+)/$', 'choose_representative'),


    # user is presented with a list of representatives whom he can write to
    (r'^(\d+)/$', 'constituency'),

    # contact a representative: write an email
    (r'^contact/(\w+)/(\d+)/$', 'contact'),

    # display a list of all public emails
    (r'^public_mails/$', 'public_mails'),

    # displays a single email. this email was sent via our site, and was marked as public
    (r'^public/(\d+)/$', 'public'),

    # feedback page
    (r'^feedback/$', 'feedback'),

    # about page
    (r'^about/$', 'about'),
    (r'^response/(\d+)/(\d+)/$', 'response'),
    (r'^i18n/', include('django.conf.urls.i18n')),
)
