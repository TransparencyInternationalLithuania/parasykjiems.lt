from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('web.views',
    url(r'^contact/$', 'contact', name='contact'),
    url(r'^contact/thanks/$', 'contact_thanks'),

    url(r'^setlang/(\w+)/$', 'setlang', name='setlang'),

    url(r'^(.+)/$', 'article', name='article'),
)
