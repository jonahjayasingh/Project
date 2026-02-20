from django.contrib import admin
from .models import MembershipRequest, TrainerRequest


@admin.register(MembershipRequest)
class MembershipRequestAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'phone_number', 'selected_plan', 'status', 'created_at']
    list_filter = ['status', 'selected_plan', 'gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth', 'gender', 'address')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Health Information', {
            'fields': ('blood_group', 'medical_notes', 'height', 'weight', 'fitness_goal')
        }),
        ('Membership Plan', {
            'fields': ('selected_plan',)
        }),
        ('Request Status', {
            'fields': ('status', 'admin_notes', 'processed_by', 'processed_at', 'created_user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(TrainerRequest)
class TrainerRequestAdmin(admin.ModelAdmin):
    list_display = ['member', 'preferred_specialization', 'sessions_per_week', 'status', 'assigned_trainer', 'created_at']
    list_filter = ['status', 'preferred_specialization', 'sessions_per_week', 'preferred_time', 'created_at']
    search_fields = ['member__user__first_name', 'member__user__last_name', 'fitness_goals']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Member Information', {
            'fields': ('member',)
        }),
        ('Trainer Preferences', {
            'fields': ('preferred_specialization', 'preferred_trainer', 'sessions_per_week', 'preferred_time')
        }),
        ('Goals & Notes', {
            'fields': ('fitness_goals', 'additional_notes')
        }),
        ('Request Status', {
            'fields': ('status', 'admin_notes', 'assigned_trainer', 'processed_by', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
