from django.contrib import admin
from search import models


class InstitutionKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'ordinal')
    list_editable = ('ordinal',)

admin.site.register(models.InstitutionKind, InstitutionKindAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'kind', 'email', 'phone')
    list_filter = ('kind',)

admin.site.register(models.Institution, InstitutionAdmin)


class RepresentativeKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'ordinal')
    list_editable = ('ordinal',)

admin.site.register(models.RepresentativeKind, RepresentativeKindAdmin)


class RepresentativeAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'kind', 'email', 'phone')
    list_filter = ('kind',)

admin.site.register(models.Representative, RepresentativeAdmin)


class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('institution',
                    'municipality',
                    'elderate',
                    'city',
                    'street',
                    'numbers',)
    ordering = list_display
    list_display_links = ('institution',)
    search_fields = ('institution__name',)


admin.site.register(models.Territory, TerritoryAdmin)
