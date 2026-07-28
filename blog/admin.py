from django.contrib import admin
from .models import BlogPost, BlogComment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'pub_date')
    search_fields = ('title', 'category', 'content')
    list_filter = ('category', 'pub_date')
    date_hierarchy = 'pub_date'

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment', 'timestamp')
    search_fields = ('comment', 'user__username', 'post__title')
    list_filter = ('timestamp',)