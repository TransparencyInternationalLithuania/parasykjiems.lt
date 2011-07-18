from django.contrib import admin
from django.utils.translation import ugettext as _
from django.db import models as djangoModel
import inspect
from territories.models import CountryAddress, LithuanianCase, InstitutionTerritory



class InstitutionTerritoryAdmin(admin.ModelAdmin):
    list_display = ['municipality', 'civilParish']
    search_fields = ['municipality', 'civilParish']

models = [CountryAddress, LithuanianCase, InstitutionTerritory]

# register custom admin models, with custom views
customModels = [(InstitutionTerritory, InstitutionTerritoryAdmin),]
for klass, adminKlas in customModels:
    admin.site.register(klass, adminKlas)

# auto-register all other models
moduleAttributes = models
moduleClasses = [m for m in moduleAttributes if inspect.isclass(m)]
modelsList = [m for m in moduleClasses if issubclass(m, djangoModel.Model)]
# from model list remove already registered models
for klass, adminKlass in customModels:
    modelsList.remove(klass)
# finally register all modules
admin.site.register(modelsList)

