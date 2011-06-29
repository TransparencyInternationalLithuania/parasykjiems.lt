#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

sentenceRegExp = u"[a-zA-Z0-9ąčęėįšųūžĄČĘĖĮŠŲŪŽ_\- \.]+"

urlpatterns = patterns('cdb_lt.views',
    # data alteration interface
    (r'^data/update/mayor/$', "mayorUpdate"),
    (r'^data/update/mayor/csv/$', "mayorUpdateAsCsv"),
    (r'^data/update/civilparish/$', "civilParishUpdate"),
    (r'^data/update/civilparish/csv/$', "civilParishUpdateAsCsv"),
    (r'^data/update/upload/$', "uploadData"),
    (r'^data/update/upload/(%(sentence)s)/$' % {'sentence' : sentenceRegExp}, 'diffUploadedFile'),
    (r'^data/update/upload/(%(sentence)s)/csv/$' % {'sentence' : sentenceRegExp}, 'diffUploadedFileAsCsv'),
    (r'^data/update/import/docs/$', 'importDocs'),
    (r'^data/update/import/(%(sentence)s)/$' % {'sentence' : sentenceRegExp}, 'importUploadedFile'),
    (r'^data/update/import/success/(%(sentence)s)/$' % {'sentence' : sentenceRegExp}, 'importUploadedFile'),

)
