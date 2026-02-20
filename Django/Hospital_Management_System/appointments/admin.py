from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'created_at']
    search_fields = ['appointment_id', 'patient__user__first_name', 'doctor__user__first_name']
    readonly_fields = ['appointment_id', 'booked_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Information', {
            'fields': ('appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'duration_minutes')
        }),
        ('Details', {
            'fields': ('reason', 'notes', 'status')
        }),
        ('Booking Information', {
            'fields': ('booked_by', 'booked_at')
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
