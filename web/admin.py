from django.contrib import admin
import models


def summary(s):
    short = s[:80]
    if short != s:
        short += '...'
    return short.replace('\n', '')


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('location', 'title', 'body_summary')
    list_display_links = list_display

    def body_summary(self, obj):
        return summary(obj.body)

admin.site.register(models.Article, ArticleAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'body_summary')
    list_display_links = list_display

    def body_summary(self, obj):
        return summary(obj.body)

admin.site.register(models.Message, MessageAdmin)
