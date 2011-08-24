from django.db import models
from django.utils.translation import ugettext_lazy as _


_NAME_LEN = 300


class Article(models.Model):
    title = models.CharField(max_length=_NAME_LEN, blank=True)
    location = models.CharField(max_length=_NAME_LEN, blank=True)
    body = models.TextField(
        help_text=_('In Markdown format.'))

    def __unicode__(self):
        return u'{}: {}'.format(self.location, self.title)
