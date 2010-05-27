from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Example:
	# (r'^parasykjiems/', include('parasykjiems.foo.urls')),

	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^polls/$', 'parasykjiems.polls.views.index'),
	(r'^polls/(?P<poll_id>\d+)/$', 'parasykjiems.polls.views.detail'),
	(r'^polls/(?P<poll_id>\d+)/results/$', 'parasykjiems.polls.views.results'),
	(r'^polls/(?P<poll_id>\d+)/vote/$', 'parasykjiems.polls.views.vote'),

	
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
)
