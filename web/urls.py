from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('web.views',
    url(r'^$', 'search'),
    url(r'^letters$', 'letters'),
    url(r'^about$', 'about'),

    url(r'^institution/(?P<inst_id>\d+)$', 'institution'),
    url(r'^representative/(?P<rep_id>\d+)$', 'representative'),

    url(r'^location/(?P<loc_id>\d+)$', 'location'),
    url(r'^location/(?P<loc_id>\d+)/(?P<house_number>\d+\w?)$', 'location'),

    url(r'^feedback$', 'feedback'),

    url(r'^setlang$', 'setlang'),
)
