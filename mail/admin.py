from django.contrib import admin
from parasykjiems.mail import models
from web.utils import summary
from django.utils.translation import ugettext_lazy as _


class UnconfirmedMessageAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'confirm_secret', 'submitted_at')
    list_display = ('submitted_at',
                    'sender_name',
                    'sender_email',
                    'recipient_name',
                    'subject',
                    'body_summary')
    ordering = ('-submitted_at',)

    def body_summary(self, obj):
        return summary(obj.body_text)
    body_summary.short_description = _('content')

admin.site.register(models.UnconfirmedMessage, UnconfirmedMessageAdmin)


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'reply_secret')
    list_display = ('date',
                    'kind',
                    'sender_name', 'recipient_name',
                    'subject',
                    'is_error',
                    'is_sent',
                    'body_summary')
    list_filter = ('is_error', 'is_sent')

    def sender(self, obj):
        return u'{} <{}>'.format(obj.sender_name, obj.sender_email)

    def recipient(self, obj):
        return u'{} <{}>'.format(obj.recipient_name, obj.recipient_email)

    def body_summary(self, obj):
        return summary(obj.body_text)
    body_summary.short_description = _('content')


admin.site.register(models.Message, MessageAdmin)


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'is_public', 'sender_name',
                    'recipient', 'subject', 'has_answer', 'has_errors')
    readonly_fields = ('messages',)
    list_filter = ('is_public',)

admin.site.register(models.Thread, ThreadAdmin)
