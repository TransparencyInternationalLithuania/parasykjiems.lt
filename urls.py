from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('views',
    url(r'^$', 'index'),

    url(r'^admin/', include(admin.site.urls)),
)
