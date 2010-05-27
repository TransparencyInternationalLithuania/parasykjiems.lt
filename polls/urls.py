from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('parasykjiems.polls.views',
	# Example:
	# (r'^parasykjiems/', include('parasykjiems.foo.urls')),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^$', 'index'),
	(r'^(?P<poll_id>\d+)/$', 'detail'),
	(r'^(?P<poll_id>\d+)/results/$', 'results'),
	(r'^(?P<poll_id>\d+)/vote/$', 'vote'),
)
