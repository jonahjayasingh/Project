from django.contrib import admin
from .models import Account, Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_balance')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'type', 'category', 'account')
    list_filter = ('type', 'category', 'account', 'date')
