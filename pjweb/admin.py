from parasykjiems.pjweb.models import Email
from django.contrib import admin

class MsgAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'subject', 'msg_state', 'email_state', 'req_date')
    
admin.site.register(Email, MsgAdmin)