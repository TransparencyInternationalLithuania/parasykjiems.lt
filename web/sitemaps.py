from django.contrib.sitemaps import Sitemap
from web.models import Article


class ArticleSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return Article.objects.all()

    def priority(self, obj):
        if obj.location in ['privacy', 'disclaimer']:
            return 0.1
        else:
            return 0.6
