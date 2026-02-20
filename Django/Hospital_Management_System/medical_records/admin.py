from django.contrib import admin
from .models import MedicalRecord, LabReport

class LabReportInline(admin.TabularInline):
    model = LabReport
    extra = 0
    readonly_fields = ['report_id', 'created_at']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'patient', 'doctor', 'created_at']
    list_filter = ['created_at', 'follow_up_required']
    search_fields = ['record_id', 'patient__user__first_name', 'diagnosis']
    readonly_fields = ['record_id', 'created_at', 'updated_at']
    inlines = [LabReportInline]
    
    fieldsets = (
        ('Record Information', {
            'fields': ('record_id', 'patient', 'doctor', 'appointment')
        }),
        ('Medical Details', {
            'fields': ('symptoms', 'diagnosis', 'treatment_plan', 'notes')
        }),
        ('Vital Signs', {
            'fields': ('temperature', 'blood_pressure', 'pulse_rate', 'respiratory_rate', 'oxygen_saturation')
        }),
        ('Follow-up', {
            'fields': ('follow_up_required', 'follow_up_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'medical_record', 'test_type', 'test_name', 'test_date']
    list_filter = ['test_type', 'test_date']
    search_fields = ['report_id', 'test_name']
    readonly_fields = ['report_id', 'created_at']
