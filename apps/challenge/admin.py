from django.contrib import admin
# Spenglr
from network.models import *
from challenge.models import *

class ChallengeAdmin(admin.ModelAdmin):
    # filter_horizontal = ('challenges',)
    raw_id_fields = ('network',)

admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(UserChallenge)
