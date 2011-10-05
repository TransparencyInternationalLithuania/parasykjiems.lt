from django.contrib import admin
from parasykjiems.mail import models


admin.site.register(models.Enquiry)
admin.site.register(models.Response)
