from django.contrib import admin
# Spenglr
from education.models import *


class NetworkAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('parent',)
    
class UserNetworkAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('network',)    

admin.site.register(Network, NetworkAdmin)
admin.site.register(UserNetwork, UserNetworkAdmin)
