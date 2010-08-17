from django.contrib import admin
# Spenglr
from network.models import *
from education.models import *


class TopicAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network','networks','concepts',)

admin.site.register(Topic, TopicAdmin)

class ConceptAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network',)

admin.site.register(Concept, ConceptAdmin)

admin.site.register(UserTopic)
admin.site.register(UserConcept)
