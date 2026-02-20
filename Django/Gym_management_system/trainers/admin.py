from django.contrib import admin
from .models import Trainer, TrainerAvailability, TrainerMemberAssignment


class TrainerAvailabilityInline(admin.TabularInline):
    model = TrainerAvailability
    extra = 1


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'experience_years', 'hourly_rate', 'is_available')
    list_filter = ('specialization', 'is_available', 'experience_years')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [TrainerAvailabilityInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('specialization', 'certifications', 'experience_years', 'hourly_rate')
        }),
        ('Bio & Availability', {
            'fields': ('bio', 'is_available')
        }),
    )


@admin.register(TrainerMemberAssignment)
class TrainerMemberAssignmentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'member', 'start_date', 'end_date', 'status', 'sessions_per_week')
    list_filter = ('status', 'start_date')
    search_fields = ('trainer__user__first_name', 'trainer__user__last_name', 'member__user__first_name', 'member__user__last_name')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('trainer', 'member', 'start_date', 'end_date', 'status')
        }),
        ('Training Plan', {
            'fields': ('sessions_per_week', 'notes')
        }),
    )
