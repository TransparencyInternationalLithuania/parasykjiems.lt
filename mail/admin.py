from django.contrib import admin
from parasykjiems.mail import models


admin.site.register(models.UnconfirmedMessage)
admin.site.register(models.Message)
admin.site.register(models.Thread)
