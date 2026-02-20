from django.contrib import admin
from .models import Medicine, Prescription, PrescriptionItem

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['medicine_id', 'name', 'generic_name', 'category', 'stock_quantity', 'unit_price', 'is_low_stock']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['medicine_id', 'name', 'generic_name', 'manufacturer']
    readonly_fields = ['medicine_id', 'created_at', 'updated_at']
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Low Stock'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'doctor', 'prescription_date', 'is_dispensed']
    list_filter = ['is_dispensed', 'prescription_date']
    search_fields = ['prescription_id', 'patient__user__first_name']
    readonly_fields = ['prescription_id', 'created_at', 'updated_at']
    inlines = [PrescriptionItemInline]

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'medicine', 'dosage', 'frequency', 'duration_days', 'quantity']
    list_filter = ['frequency']
    search_fields = ['medicine__name', 'prescription__prescription_id']
