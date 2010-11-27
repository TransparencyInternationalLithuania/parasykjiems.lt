from parasykjiems.pjweb.models import Email, MailHistory
from django.contrib import admin
from django.utils.translation import ugettext as _

class MsgAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Recipient'), {'fields': ['recipient_name']}),
        (_('Sender Information'), {'fields': ['sender_name', 'sender_mail']}),
        (_('Message'),            {'fields': ['message', 'msg_state', 'public']}),
    ]
    list_display = ('sender_name', 'msg_state', 'mail_date', 'public')
    list_filter = ['mail_date', 'sender_mail', 'recipient_mail']
    search_fields = ['recipient_name', 'sender_name', 'recipient_mail', 'sender_mail']
    date_hierarchy = 'mail_date'
    
admin.site.register(Email, MsgAdmin)

class MsgHistAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Recipients'), {'fields': ['recipient', 'sender']}),
        (_('States'),     {'fields': ['mail', 'mail_state']}),
    ]
    list_display = ('sender', 'recipient', 'mail_state', 'request_date')
    list_filter = ['request_date', 'sender', 'recipient']
    search_fields = ['recipient', 'sender']
    date_hierarchy = 'request_date'

admin.site.register(MailHistory, MsgHistAdmin)
