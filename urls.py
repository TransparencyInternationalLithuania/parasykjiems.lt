from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    url(r'', include('search.urls')),
    url(r'', include('mail.urls')),

    url(r'^admin/', include(admin.site.urls)),

    # This should be the last in the list, because the
    # web.views.article's URL is sort of catch-all.
    url(r'', include('web.urls')),
)
