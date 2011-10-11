from django.contrib.sitemaps import Sitemap
from models import Thread


class ThreadSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Thread.objects.filter(is_open=True)

    def lastmod(self, obj):
        return obj.modified_at
