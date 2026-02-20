from django.contrib import admin
from .models import Patient, PatientDocument

class PatientDocumentInline(admin.TabularInline):
    model = PatientDocument
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'get_full_name', 'blood_group', 'status', 'created_at']
    list_filter = ['status', 'blood_group', 'created_at']
    search_fields = ['patient_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']
    inlines = [PatientDocumentInline]
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_id', 'user', 'blood_group', 'height', 'weight')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')
        }),
        ('Medical History', {
            'fields': ('allergies', 'chronic_conditions', 'current_medications', 'past_surgeries')
        }),
        ('Status', {
            'fields': ('status', 'admission_date', 'discharge_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'document_type', 'title', 'uploaded_by', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['patient__patient_id', 'title']
    readonly_fields = ['uploaded_at']
