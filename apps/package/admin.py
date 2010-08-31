from django.contrib import admin
# Spenglr
from network.models import *
from package.models import *


class PackageAdmin(admin.ModelAdmin):
    # filter_horizontal = ('challenges',)
    raw_id_fields = ('network','networks','challenges',)

admin.site.register(Package, PackageAdmin)


admin.site.register(UserPackage)

