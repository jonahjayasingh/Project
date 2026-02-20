from django.contrib import admin
from .models import Department, Doctor

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_of_department', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['doctor_id', 'get_full_name', 'specialization', 'department', 'status', 'consultation_fee']
    list_filter = ['status', 'department', 'created_at']
    search_fields = ['doctor_id', 'user__first_name', 'user__last_name', 'specialization', 'license_number']
    readonly_fields = ['doctor_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Doctor Information', {
            'fields': ('doctor_id', 'user', 'department', 'specialization', 'license_number')
        }),
        ('Professional Details', {
            'fields': ('qualifications', 'experience_years', 'consultation_fee')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_time_start', 'available_time_end', 'status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
