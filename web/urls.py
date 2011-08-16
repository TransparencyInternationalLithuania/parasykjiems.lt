from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('web.views',
    url(r'^about/$', 'about', name='about'),
    url(r'^help/$', 'help_view', name='help'),

    url(r'^feedback/$', 'feedback', name='feedback'),
    url(r'^feedback/thanks/$', 'feedback_thanks'),

    url(r'^setlang/(\w+)/$', 'setlang'),
)
