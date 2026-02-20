from django.contrib import admin
from .models import MembershipPlan, MemberMembership


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_months', 'price', 'access_level', 'is_active')
    list_filter = ('duration_months', 'access_level', 'is_active')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'description', 'duration_months', 'price')
        }),
        ('Access & Benefits', {
            'fields': ('access_level', 'benefits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(MemberMembership)
class MemberMembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'plan', 'start_date', 'end_date', 'status', 'payment_status', 'days_remaining')
    list_filter = ('status', 'payment_status', 'start_date', 'end_date')
    search_fields = ('member__user__username', 'member__user__email', 'member__user__first_name', 'member__user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'days_remaining')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Membership Info', {
            'fields': ('member', 'plan', 'start_date', 'end_date', 'status')
        }),
        ('Payment', {
            'fields': ('payment_status', 'amount_paid')
        }),
        ('Freeze Information', {
            'fields': ('freeze_start_date', 'freeze_end_date'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def days_remaining(self, obj):
        return obj.days_remaining()
    days_remaining.short_description = 'Days Remaining'
