from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('web.views',
    url(r'^$', 'index'),
    url(r'^letters$', 'letters'),
    url(r'^about$', 'about'),

    url(r'^institution/(?P<id>\d+)$', 'institution'),
    url(r'^representative/(?P<id>\d+)$', 'representative'),
    url(r'^location/(?P<id>\d+)$', 'location'),
    url(r'^location/(?P<id>\d+)/(?P<house_number>\d+\w?)$', 'location'),

    url(r'^write_to/(?P<type>\w+)/(?P<id>\d+)$', 'write_to'),

    url(r'^setlang$', 'setlang'),
)
