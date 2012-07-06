from django.contrib import admin
from django.db.models import TextField
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _
from web.utils import summary
import models


class ArticleAdmin(admin.ModelAdmin):
    exclude = ('body_rendered',)
    formfield_overrides = {
        TextField: {
            'widget': Textarea(
                attrs={
                    'rows': '30',
                    'cols': '90'})}}

    list_display = ('location', 'title', 'body_summary')
    ordering = ('location', 'title')

    def body_summary(self, obj):
        return summary(obj.body)
    body_summary.short_description = _('content')

admin.site.register(models.Article, ArticleAdmin)

