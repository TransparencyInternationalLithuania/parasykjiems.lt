from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('search.views',
    url(r'^$', 'search', name='search'),
    url(r'^autocomplete/$', 'autocomplete', name='autocomplete'),

    url(r'^institution/(?P<slug>[\w-]+)/$', 'institution',
        name='institution'),
    url(r'^representative/(?P<slug>[\w-]+)/$', 'representative',
        name='representative'),

    url(r'^location/(?P<slug>[\w-]+)/$', 'location', name='location'),
    url(r'^location/(?P<slug>[\w-]+)/ask/$', 'location_ask'),
    url(r'^location/(?P<slug>[\w-]+)/(?P<house_number>\d+\w?)/$', 'location'),
)
