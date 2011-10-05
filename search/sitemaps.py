from django.contrib.sitemaps import Sitemap
from search.models import Institution


class InstitutionSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Institution.objects.all()
