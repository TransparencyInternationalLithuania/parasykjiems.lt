from django.conf.urls.defaults import patterns, url
import feeds

urlpatterns = patterns('mail.views',
    url(r'^write/representative/(?P<slug>[\w-]+)/$', 'write_representative',
        name='write-representative'),
    url(r'^write/institution/(?P<slug>[\w-]+)/$', 'write_institution',
        name='write-institution'),
    url(r'^write/confirm/$', 'write_confirm'),

    url(r'^confirm/(?P<id>\d+)/(?P<confirm_secret>\d+)/$', 'confirm',
        name='confirm'),

    url(r'^sent/$', 'sent'),
    url(r'^sent/(?P<slug>[\w-]+)/$', 'sent'),

    url(r'^threads/$', 'threads', name='threads'),
    url(r'^threads/rss.xml$', feeds.ThreadsFeed()),

    url(r'^threads/(?P<institution_slug>[\w-]+)/$', 'threads_institution'),

    url(r'^thread/(?P<slug>[\w-]+)/$', 'thread', name='thread'),
    url(r'^thread/(?P<slug>[\w-]+)/rss.xml$', feeds.ThreadFeed()),
)
