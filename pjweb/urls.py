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
    (r'^contact/(\w+)/(\w+)/thanks/$', 'thanks'),
    (r'^contact/(\w+)/no_email/$', 'no_email'),
    (r'^contact/(\w+)/(\w+)/(\w+)/smtp_error/$', 'smtp_error'),
    #(r'^contact/(\w+)/(\d+)/select_privacy/$', 'select_privacy'),
    (r'^(\d+)/(\w+)/$', 'constituency'),
    (r'^contact/(\w+)/(\d+)/$', 'contact'),
    (r'^public_mails/$', 'public_mails'),
    (r'^public/(\d+)/$', 'public'),

    #(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
)
