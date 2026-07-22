from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import BlogPost, BlogComment

# Register your models here.
admin.site.register(BlogPost)
admin.site.register(BlogComment)