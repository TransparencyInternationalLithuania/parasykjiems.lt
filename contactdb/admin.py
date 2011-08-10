from contactdb import models
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.db import models as djangoModel
import inspect
from contactdb.models import PersonPosition

class PersonPositionAdmin(admin.ModelAdmin):
    list_display = ('institution', 'person', 'email', 'electedFrom', 'electedTo')
    search_fields = ['institution__name', 'person__name', 'email']

# register custom admin models, with custom views
customModels = [(PersonPosition, PersonPositionAdmin)]
for klass, adminKlas in customModels:
    admin.site.register(klass, adminKlas)

# auto-register all other models
moduleAttributes = [getattr(models, m) for m in dir(models)]
moduleClasses = [m for m in moduleAttributes if inspect.isclass(m)]
modelsList = [m for m in moduleClasses if issubclass(m, djangoModel.Model)]
# from model list remove already registered models
for klass, adminKlass in customModels:
    modelsList.remove(klass)
# finally register all modules
admin.site.register(modelsList)

