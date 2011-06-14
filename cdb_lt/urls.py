#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('cdb_lt.views',
    # data alteration interface
    (r'^data/update/mayor/$', "mayorUpdate"),
    (r'^data/update/mayor/csv/$', "mayorUpdateAsCsv"),
    (r'^data/update/civilparish/$', "civilParishUpdate"),
    (r'^data/update/civilparish/csv/$', "civilParishUpdateAsCsv"),
    (r'^data/update/upload/$', "uploadData"),

)
