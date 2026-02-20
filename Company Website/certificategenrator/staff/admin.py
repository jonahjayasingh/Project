from django.contrib import admin
from .models import *
# Register your models here.
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'date')

class WorkAdmin(admin.ModelAdmin):
    list_display = ("user","time_slot","work","date")
    
admin.site.register(Attendance,AttendanceAdmin)
admin.site.register(Work,WorkAdmin)

