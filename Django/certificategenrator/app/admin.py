from django.contrib import admin
from .models import *
# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_no', 'course_name', 'faculty_name', 'joined_date', "certificate_id","completed_date")
    search_fields = ('name', 'registration_no', 'course_name',"joined_date")
    list_filter = ('certificate_id',)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user__name', 'paid_ammount')

    search_fields = ('user__name', 'paid_ammount')

admin.site.register(Student, StudentAdmin)
admin.site.register(StaffPermission)
admin.site.register(Receipt)
admin.site.register(Payment,PaymentAdmin)
admin.site.register(Transaction)
admin.site.register(Account)
admin.site.register(Constant_Value)
admin.site.register(StaffDetails)
admin.site.register(CourseName)