from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'join_date', 'status', 'blood_group', 'emergency_contact_name')
    list_filter = ('status', 'join_date', 'blood_group')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'emergency_contact_name')
    readonly_fields = ('join_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'status', 'join_date')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Health Information', {
            'fields': ('blood_group', 'height', 'weight', 'medical_notes')
        }),
        ('Fitness', {
            'fields': ('fitness_goal',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
