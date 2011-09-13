from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
import models


def summary(s):
    short = s[:80]
    if short != s:
        short += '...'
    return short.replace('\n', '')


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('location', 'title', 'body_summary')
    ordering = ('location', 'title')

    def body_summary(self, obj):
        return summary(obj.body)
    body_summary.short_description = _('content')

admin.site.register(models.Article, ArticleAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_summary')
    ordering = ('name',)

    def body_summary(self, obj):
        return summary(obj.body)
    body_summary.short_description = _('content')

admin.site.register(models.Message, MessageAdmin)
