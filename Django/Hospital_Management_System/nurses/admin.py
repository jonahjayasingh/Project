from django.contrib import admin
from .models import Nurse, NursePatientAssignment

@admin.register(Nurse)
class NurseAdmin(admin.ModelAdmin):
    list_display = ['nurse_id', 'get_full_name', 'department', 'shift', 'status']
    list_filter = ['status', 'shift', 'department', 'created_at']
    search_fields = ['nurse_id', 'user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['nurse_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(NursePatientAssignment)
class NursePatientAssignmentAdmin(admin.ModelAdmin):
    list_display = ['nurse', 'patient', 'assigned_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'assigned_date']
    search_fields = ['nurse__user__first_name', 'patient__user__first_name']
