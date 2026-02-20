from django.contrib import admin

# Register your models here.
from .models import JobPost,JobSeekerProfile,CompanyProfile

class JobPostAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'job_type', 'experience', 'salary', 'posted_at', 'is_active')
    list_filter = ('job_type', 'experience', 'is_active')
    search_fields = ('job_title', 'company')

admin.site.register(JobSeekerProfile)
admin.site.register(CompanyProfile)
admin.site.register(JobPost,JobPostAdmin)
