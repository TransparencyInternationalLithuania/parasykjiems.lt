from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember
from django.contrib import admin
from django.utils.translation import ugettext as _

class AddrAdmin(admin.ModelAdmin):

    list_display = ('street', 'city', 'district')
    
admin.site.register(PollingDistrictStreet, AddrAdmin)

class MPAdmin(admin.ModelAdmin):

    list_display = ('name', 'surname', 'email')
    
admin.site.register(ParliamentMember, MPAdmin)

class ConstAdmin(admin.ModelAdmin):

    list_display = ('name', 'nr')
    
admin.site.register(Constituency, ConstAdmin)