from django.contrib import admin
from .models import StudentDetails

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone', 'address', 'date_of_birth', 'gender', 'blood_group', 'profile_picture', 'course', 'branch', 'year', 'sem', 'roll_no', 'reg_no', 'cgpa')
    search_fields = ('name', 'email', 'phone', 'roll_no', 'reg_no')


admin.site.register(StudentDetails, StudentAdmin)

