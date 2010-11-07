from parasykjiems.pjweb.models import Email
from django.contrib import admin
from django.utils.translation import ugettext as _

class MsgAdmin(admin.ModelAdmin):
    fieldsets = [
        (_('Recipient'), {'fields': ['recipient_name']}),
        (_('Sender Information'), {'fields': ['sender_name', 'sender']}),
        (_('Message'),            {'fields': ['phone', 'message', 'msg_state', 'public']}),
    ]
    list_display = ('sender_name', 'phone', 'msg_state', 'email_state', 'req_date', 'public')
    
admin.site.register(Email, MsgAdmin)
