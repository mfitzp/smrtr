from django.contrib import admin
from spenglr.education.models import *


admin.site.register(Network)
admin.site.register(Qualification)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Exam)

admin.site.register(UserNetwork)
admin.site.register(UserQualification)
admin.site.register(UserCourse)
admin.site.register(UserModule)
admin.site.register(UserExam)