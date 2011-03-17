from contactdb import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.db import models as djangoModel
import inspect

"""
class AddrAdmin(admin.ModelAdmin):
    list_display = ('street', 'city')

class MPAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email')
    
class ConstAdmin(admin.ModelAdmin):
    list_display = ('name', 'nr')

# register custom admin models, with custom views
customModels = [(PollingDistrictStreet, AddrAdmin), (ParliamentMember, MPAdmin), (Constituency, ConstAdmin)]
for klass, adminKlas in customModels:
    admin.site.register(klass, adminKlas)
    """

# auto-register all other models
"""moduleAttributes = [getattr(models, m) for m in dir(models)]
moduleClasses = [m for m in moduleAttributes if inspect.isclass(m)]
modelsList = [m for m in moduleClasses if issubclass(m, djangoModel.Model)]
# from model list remove already registered models
for klass, adminKlass in customModels:
    modelsList.remove(klass)
# finally register all modules
admin.site.register(modelsList)
"""
