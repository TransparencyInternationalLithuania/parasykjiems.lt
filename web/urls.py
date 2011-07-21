from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('web.views',
    url(r'^$', 'index'),
    url(r'^mail$', 'mail'),
    url(r'^about$', 'about'),

    url(r'^setlang$', 'setlang'),
)
