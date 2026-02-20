from django.contrib import admin
from .models import Post, Comment, UserProfile

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'status', 'created_on')
    list_filter = ("status",)
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_on', 'is_removed')
    list_filter = ('is_removed', 'created_on')
    search_fields = ('content',)

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile)
