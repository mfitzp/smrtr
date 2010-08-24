from django.contrib import admin
# Spenglr
from network.models import *
from concept.models import *

class ConceptAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network',)

admin.site.register(Concept, ConceptAdmin)
admin.site.register(UserConcept)
