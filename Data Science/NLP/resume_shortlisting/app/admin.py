from django.contrib import admin

# Register your models here.
from .models import JobPost,JobApplication,JobSeekerProfile,CompanyProfile

class JobPostAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'company', 'job_type', 'experience', 'salary', 'posted_at', 'is_active')
    list_filter = ('job_type', 'experience', 'is_active')
    search_fields = ('job_title', 'company__name')

class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'job_seeker', 'resume', 'applied_at')
    list_filter = ('job__job_type', 'job__experience')
    search_fields = ('job__job_title', 'job_seeker__user__username')
    actions = ['approve_applications', 'reject_applications']

    

admin.site.register(JobApplication,JobApplicationAdmin)
admin.site.register(JobSeekerProfile)
admin.site.register(CompanyProfile)
admin.site.register(JobPost,JobPostAdmin)
