from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('search.views',
    url(r'^$', 'search', name='search'),

    url(r'^institution/(?P<id>[\w-]+)$', 'institution',
        name='institution'),
    url(r'^representative/(?P<id>[\w-]+)$', 'representative',
        name='representative'),

    url(r'^location/(?P<id>[\w-]+)$', 'location', name='location'),
    url(r'^location/(?P<id>[\w-]+)/ask$', 'location_ask'),
    url(r'^location/(?P<id>[\w-]+)/(?P<house_number>\d+\w?)$', 'location'),
)
