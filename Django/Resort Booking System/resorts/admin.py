from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Resort, Room, Booking

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(Resort)
admin.site.register(Room)
admin.site.register(Booking)
