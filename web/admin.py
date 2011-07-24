from django.contrib import admin
import web.models

admin.site.register(web.models.InstitutionKind)
admin.site.register(web.models.Institution)
admin.site.register(web.models.RepresentativeKind)
admin.site.register(web.models.Representative)
admin.site.register(web.models.Territory)
