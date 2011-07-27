from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('search.views',
    url(r'^$', 'search', name='search'),

    url(r'^institution/(?P<inst_id>\d+)$', 'institution', name='institution'),
    url(r'^representative/(?P<rep_id>\d+)$', 'representative', name='representative'),

    url(r'^location/(?P<loc_id>\d+)$', 'location', name='location'),
    url(r'^location/(?P<loc_id>\d+)/ask$', 'location_ask'),
    url(r'^location/(?P<loc_id>\d+)/(?P<house_number>\d+\w?)$', 'location'),
)
