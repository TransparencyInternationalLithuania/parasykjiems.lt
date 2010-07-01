from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('parasykjiems.pjweb.views',
    # Example:
    # (r'^parasykjiems/', include('parasykjiems.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^$', 'index'),
    (r'^thanks/$', 'thanks'),
    (r'^contact/$', 'contact'),
    (r'^contact/smtp_error/$', 'smtp_error'),
    (r'^(?P<constituency_id>\d+)/$', 'constituency'),
    #(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
)
