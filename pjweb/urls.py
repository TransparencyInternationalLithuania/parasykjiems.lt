#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from pjweb.rss_feed.rss_feed import PublicMailsFeed

admin.autodiscover()

urlpatterns = patterns('pjweb.views',
    # Example:
    # (r'^parasykjiems/', include('parasykjiems.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Handle start page
    (r'^$', 'index'),

    (u'^choose_rep_civilparish/([^/]+)/([^/]+)/([^/]+)/$', 'choose_representative_civil_parish'),
    (u'^choose_rep/([^/]+)/([^/]+)/$', 'choose_representative'),
    (u'^choose_rep/([^/]+)/([^/]+)/([^/]+)/$', 'choose_representative'),
    (u'^choose_rep/([^/]+)/([^/]+)/([^/]+)/([^/]+)/$', 'choose_representative'),

    # contact a representative: write an email
    (r'^contact/([^/]+)/(\d+)/$', 'contact'),
    (r'^contact/([^/]+)/(\d+)/no_email/$', 'no_email'),

    # display a list of all public emails
    (r'^public/$', 'public_mails'),

    # displays a single email. this email was sent via our site, and was marked as public
    (r'^public/(\d+)/$', 'public'),

    # feedback page
    (r'^feedback/$', 'feedback'),

    # about page
    (r'^about/$', 'about'),
    (r'^stats/$', 'stats'),
    (r'^response/(\d+)/(\d+)/$', 'response'),
    (r'^confirm/(\d+)/(\d+)/$', 'confirm'),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^setlang/(?P<lang_code>.*)/$', 'set_language'),

    # RSS feeds
    (r'^public/rss/$', PublicMailsFeed()),
    #(r'^public/(?P<mail_id>\d+)/rss/$', SingleMailFeed()),
)
