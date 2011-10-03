from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('scrape.views',
    url(r'^admin/update/$', 'admin_update'),
)
