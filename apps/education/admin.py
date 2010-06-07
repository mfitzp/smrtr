from django.contrib import admin
# Spenglr
from network.models import *
from education.models import *


class ModuleAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network','networks','concepts',)

admin.site.register(Module, ModuleAdmin)

class ConceptAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network',)

admin.site.register(Concept, ConceptAdmin)

admin.site.register(UserModule)
admin.site.register(UserConcept)
