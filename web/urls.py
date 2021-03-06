from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('web.views',
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^contact/thanks/$', 'contact_thanks'),

    url(r'^robots.txt$', 'robots_txt'),

    url(r'^(.+)/$', 'article', name='article'),
)
