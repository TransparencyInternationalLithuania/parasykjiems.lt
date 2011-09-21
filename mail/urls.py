from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('mail.views',
    url(r'^write/representative/(?P<slug>[\w-]+)/$', 'write_representative',
        name='write-representative'),
    url(r'^write/institution/(?P<slug>[\w-]+)/$', 'write_institution',
        name='write-institution'),
    url(r'^write/confirm/$', 'write_confirm'),

    url(r'^confirm/(?P<id>\d+)/(?P<confirm_hash>\d+)/$', 'confirm',
        name='confirm'),
    url(r'^sent/(?P<id>\d+)/$', 'sent'),

    url(r'^thread/(?P<slug>[\w-]+)/$', 'thread', name='thread'),

    url(r'^letters/$', redirect_to, {'url': '/threads/'}, name='letters'),

    url(r'^threads/$', 'threads', name='threads'),
    url(r'^threads/(?P<institution_slug>[\w-]+)/$', 'threads', name='threads'),
)
