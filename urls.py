from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import web.sitemaps
import search.sitemaps
import mail.sitemaps


admin.autodiscover()


sitemaps = {
    'articles': web.sitemaps.ArticleSitemap,
    'institutions': search.sitemaps.InstitutionSitemap,
    'threads': mail.sitemaps.ThreadSitemap,
}


urlpatterns = patterns('',
    url(r'', include('search.urls')),
    url(r'', include('mail.urls')),

    url(r'', include('scrape.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),

    # This should be the last in the list, because the
    # web.views.article's URL is sort of catch-all.
    url(r'', include('web.urls')),
)
