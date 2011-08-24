from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('web.views',
    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^feedback/thanks/$', 'feedback_thanks'),

    url(r'^setlang/(\w+)/$', 'setlang', name='setlang'),

    url(r'^(.+)/$', 'article', name='article'),
)
