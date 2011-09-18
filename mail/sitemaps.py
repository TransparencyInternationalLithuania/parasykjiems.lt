from django.contrib.sitemaps import Sitemap
from models import Enquiry


class ThreadSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Enquiry.objects.filter(parent=None,
                                      is_sent=True,
                                      is_open=True)

    def lastmod(self, obj):
        # TODO: Should return date of last message in thread, not
        # first.
        return obj.date
