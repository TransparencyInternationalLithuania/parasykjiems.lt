from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('mail.views',
    url(r'^write/representative/(?P<id>\d+)$', 'write_representative',
        name='write-representative'),
    url(r'^write/institution/(?P<id>\d+)$', 'write_institution',
        name='write-institution'),
    url(r'^write/confirm$', 'write_confirm'),

    url(r'^confirm/(?P<unique_hash>\d+)$', 'confirm', name='confirm'),
    url(r'^sent/(?P<id>\d+)$', 'sent'),

    url(r'^letter/(?P<id>\d+)$', 'letter', name='letter'),

    url(r'^letters$', 'letters', name='letters'),
)
