from django.contrib import admin
from .models import Room, Bed, Admission

class BedInline(admin.TabularInline):
    model = Bed
    extra = 1

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'cost_per_day', 'total_beds', 'available_beds', 'is_active']
    list_filter = ['room_type', 'floor', 'is_active']
    search_fields = ['room_number']
    inlines = [BedInline]

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['bed_number', 'room', 'is_occupied', 'is_active']
    list_filter = ['is_occupied', 'is_active', 'room__room_type']
    search_fields = ['bed_number', 'room__room_number']

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['admission_id', 'patient', 'bed', 'admission_date', 'discharge_date', 'status', 'duration_days']
    list_filter = ['status', 'admission_date']
    search_fields = ['admission_id', 'patient__user__first_name']
    readonly_fields = ['admission_id', 'duration_days', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Admission Information', {
            'fields': ('admission_id', 'patient', 'bed', 'reason', 'status')
        }),
        ('Dates', {
            'fields': ('admission_date', 'discharge_date', 'duration_days')
        }),
        ('Staff', {
            'fields': ('admitted_by', 'discharged_by')
        }),
        ('Discharge Information', {
            'fields': ('discharge_summary', 'discharge_instructions'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
