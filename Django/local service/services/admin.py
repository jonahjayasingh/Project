from django.contrib import admin
from .models import Category, ServiceProvider

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_approved', 'is_active', 'rating')
    list_filter = ('is_approved', 'is_active', 'categories')
    search_fields = ('name', 'location')
    actions = ['approve_providers']

    def approve_providers(self, request, queryset):
        queryset.update(is_approved=True)
    approve_providers.short_description = "Approve selected providers"
