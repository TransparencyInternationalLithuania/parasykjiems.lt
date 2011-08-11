from django.contrib import admin
from search import models


class InstitutionKindAdmin(admin.ModelAdmin):
    list_display = ('name', 'ordinal')
    list_editable = ('ordinal',)

admin.site.register(models.InstitutionKind, InstitutionKindAdmin)


admin.site.register(models.Institution)
admin.site.register(models.RepresentativeKind)
admin.site.register(models.Representative)


class TerritoryAdmin(admin.ModelAdmin):
    list_display = ('institution',
                    'municipality',
                    'elderate',
                    'city',
                    'street',
                    'numbers',
                    )
    list_display_links = ('institution',)
    list_editable = ('municipality',
                    'elderate',
                    'city',
                    'street',
                     )

    search_fields = ('municipality',
                     'elderate',
                     'city',
                     'street',
                     )


admin.site.register(models.Territory, TerritoryAdmin)
