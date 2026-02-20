from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Student, Book, BorrowRecord


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'name', 'email', 'department', 'class_name', 'date_created', 'get_borrowed_count']
    list_filter = ['department', 'class_name', 'date_created']
    search_fields = ['student_number', 'name', 'email']
    readonly_fields = ['student_number', 'date_created']
    
    fieldsets = (
        ('Student Information', {
            'fields': ('student_number', 'name', 'email', 'department', 'class_name')
        }),
        ('Account', {
            'fields': ('user',)
        }),
        ('Settings', {
            'fields': ('max_books_allowed', 'date_created')
        }),
    )
    
    def get_borrowed_count(self, obj):
        return obj.get_borrowed_books_count()
    get_borrowed_count.short_description = 'Books Borrowed'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'total_copies', 'available_copies', 'is_available', 'date_added']
    list_filter = ['date_added']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['date_added']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'description')
        }),
        ('Inventory', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Metadata', {
            'fields': ('date_added',)
        }),
    )


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'book', 'borrow_date', 'due_date', 'return_date', 'status', 'is_overdue']
    list_filter = ['status', 'borrow_date', 'due_date']
    search_fields = ['student__student_number', 'student__name', 'book__title']
    readonly_fields = ['borrow_date']
    date_hierarchy = 'borrow_date'
    
    fieldsets = (
        ('Borrow Information', {
            'fields': ('student', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('borrow_date', 'due_date', 'return_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
