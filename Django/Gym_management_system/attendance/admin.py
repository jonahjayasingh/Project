from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'date', 'check_in_time', 'check_out_time', 'attendance_type', 'duration_display')
    list_filter = ('attendance_type', 'date', 'check_in_time')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'member__user__username')
    date_hierarchy = 'date'
    readonly_fields = ('check_in_time', 'duration_display')
    
    fieldsets = (
        ('Member & Date', {
            'fields': ('member', 'date', 'attendance_type')
        }),
        ('Time', {
            'fields': ('check_in_time', 'check_out_time', 'duration_display')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        duration = obj.duration()
        if duration:
            return f"{duration} hours"
        return "Still checked in"
    duration_display.short_description = 'Duration'
    
    actions = ['check_out_members']
    
    def check_out_members(self, request, queryset):
        from django.utils import timezone
        count = 0
        for attendance in queryset:
            if not attendance.is_checked_out():
                attendance.check_out_time = timezone.now()
                attendance.save()
                count += 1
        self.message_user(request, f"{count} members checked out.")
    check_out_members.short_description = "Check out selected members"
