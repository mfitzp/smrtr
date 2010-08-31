from django.contrib import admin
# Smrtr
from network.models import *


class NetworkAdmin(admin.ModelAdmin):
    # filter_horizontal = ('challenges',)
    raw_id_fields = ('parent',)
    
class UserNetworkAdmin(admin.ModelAdmin):
    # filter_horizontal = ('challenges',)
    raw_id_fields = ('network',)    

admin.site.register(Network, NetworkAdmin)
admin.site.register(UserNetwork, UserNetworkAdmin)
