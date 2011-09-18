from django.contrib.sitemaps import Sitemap
from web.models import Article


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Article.objects.all()
