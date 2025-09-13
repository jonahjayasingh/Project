from django.contrib import admin
from .models import Events,Gallery,Profile,Mcq,Question
# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_display = ('question','option1','option2','option3','option4','answer','mcq')

admin.site.register(Events)
admin.site.register(Gallery)
admin.site.register(Profile)

admin.site.register(Mcq)
admin.site.register(Question,QuestionAdmin)
