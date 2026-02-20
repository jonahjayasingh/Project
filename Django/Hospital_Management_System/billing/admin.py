from django.contrib import admin
from .models import Bill, Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_id', 'payment_date']

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_id', 'patient', 'total_amount', 'amount_paid', 'balance_due', 'payment_status', 'created_at']
    list_filter = ['payment_status', 'created_at']
    search_fields = ['bill_id', 'patient__user__first_name']
    readonly_fields = ['bill_id', 'subtotal', 'total_amount', 'balance_due', 'created_at', 'updated_at']
    inlines = [PaymentInline]
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('bill_id', 'patient', 'appointment')
        }),
        ('Charges', {
            'fields': ('consultation_fee', 'medicine_charges', 'room_charges', 'lab_charges', 'other_charges', 'discount', 'tax')
        }),
        ('Totals', {
            'fields': ('subtotal', 'total_amount', 'amount_paid', 'balance_due')
        }),
        ('Payment Information', {
            'fields': ('payment_status', 'payment_method')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'bill', 'amount', 'payment_method', 'payment_date', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['payment_id', 'bill__bill_id', 'transaction_id']
    readonly_fields = ['payment_id', 'payment_date']
