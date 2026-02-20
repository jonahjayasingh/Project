from django.contrib import admin
from .models import Payment, Invoice


class InvoiceInline(admin.StackedInline):
    model = Invoice
    extra = 0
    readonly_fields = ('generated_date',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'member', 'amount', 'payment_method', 'payment_type', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_type', 'payment_date')
    search_fields = ('invoice_number', 'member__user__first_name', 'member__user__last_name', 'transaction_id')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    inlines = [InvoiceInline]
    
    fieldsets = (
        ('Payment Details', {
            'fields': ('invoice_number', 'member', 'amount', 'payment_date')
        }),
        ('Payment Info', {
            'fields': ('payment_method', 'payment_type', 'status', 'transaction_id')
        }),
        ('Additional', {
            'fields': ('description', 'received_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected as Completed"
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')
        self.message_user(request, f"{queryset.count()} payments marked as refunded.")
    mark_as_refunded.short_description = "Mark selected as Refunded"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('payment', 'generated_date')
    search_fields = ('payment__invoice_number', 'payment__member__user__first_name', 'payment__member__user__last_name')
    readonly_fields = ('generated_date',)
