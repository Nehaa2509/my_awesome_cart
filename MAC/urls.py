"""
URL configuration for MAC project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop import views as shop_views

# Custom Django Admin Header & Title Branding
admin.site.site_header = "My Awesome Cart Admin"
admin.site.site_title = "MyAwesomeCart Admin"
admin.site.index_title = "Dashboard"

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),
    path('blog/', include('blog.urls')),
    path('', shop_views.index, name='Home'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

