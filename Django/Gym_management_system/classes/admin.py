from django.contrib import admin
from .models import FitnessClass, ClassSchedule, ClassBooking


class ClassScheduleInline(admin.TabularInline):
    model = ClassSchedule
    extra = 1
    fields = ('day_of_week', 'start_time', 'trainer', 'room_location', 'is_active')


@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty_level', 'duration_minutes', 'capacity', 'is_active')
    list_filter = ('difficulty_level', 'is_active')
    search_fields = ('name', 'description')
    inlines = [ClassScheduleInline]
    
    fieldsets = (
        ('Class Details', {
            'fields': ('name', 'description', 'difficulty_level', 'duration_minutes')
        }),
        ('Capacity & Image', {
            'fields': ('capacity', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('fitness_class', 'day_of_week', 'start_time', 'trainer', 'room_location', 'get_current_bookings', 'is_active')
    list_filter = ('day_of_week', 'is_active', 'fitness_class')
    search_fields = ('fitness_class__name', 'trainer__user__first_name', 'trainer__user__last_name')
    
    def get_current_bookings(self, obj):
        return f"{obj.get_current_bookings_count()}/{obj.fitness_class.capacity}"
    get_current_bookings.short_description = 'Bookings'


@admin.register(ClassBooking)
class ClassBookingAdmin(admin.ModelAdmin):
    list_display = ('member', 'schedule', 'booking_date', 'status', 'attended')
    list_filter = ('status', 'attended', 'booking_date')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'schedule__fitness_class__name')
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Details', {
            'fields': ('schedule', 'member', 'status')
        }),
        ('Attendance', {
            'fields': ('attended', 'notes')
        }),
    )
    
    actions = ['mark_as_attended', 'mark_as_no_show', 'cancel_bookings']
    
    def mark_as_attended(self, request, queryset):
        queryset.update(status='attended', attended=True)
        self.message_user(request, f"{queryset.count()} bookings marked as attended.")
    mark_as_attended.short_description = "Mark selected as Attended"
    
    def mark_as_no_show(self, request, queryset):
        queryset.update(status='no_show', attended=False)
        self.message_user(request, f"{queryset.count()} bookings marked as no show.")
    mark_as_no_show.short_description = "Mark selected as No Show"
    
    def cancel_bookings(self, request, queryset):
        for booking in queryset:
            booking.cancel_booking()
        self.message_user(request, f"{queryset.count()} bookings cancelled.")
    cancel_bookings.short_description = "Cancel selected bookings"
