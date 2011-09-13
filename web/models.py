from django.db import models
from django.utils.translation import ugettext_lazy as _


_NAME_LEN = 300


class Article(models.Model):
    title = models.CharField(max_length=_NAME_LEN,
                             verbose_name=_('title'))
    location = models.CharField(max_length=_NAME_LEN,
                                unique=True,
                                db_index=True,
                                verbose_name=_('article location'))
    body = models.TextField(
        help_text=_('In Markdown format.'),
        verbose_name=_('content'))

    def __unicode__(self):
        return u'{}: {}'.format(self.location, self.title)

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')


class Message(models.Model):
    name = models.CharField(max_length=_NAME_LEN,
                            unique=True,
                            db_index=True,
                            verbose_name=_('message identifier'))
    body = models.TextField(
        help_text=_('In Markdown format.'),
        blank=True,
        verbose_name=_('content'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
