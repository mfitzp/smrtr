from django.contrib import admin
from discuss.models import *

admin.site.register(Forum)


class ThreadAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('forum',)
admin.site.register(Thread, ThreadAdmin)

class PostAdmin(admin.ModelAdmin):
    # filter_horizontal = ('concepts',)
    raw_id_fields = ('thread',)
admin.site.register(Post, PostAdmin)

