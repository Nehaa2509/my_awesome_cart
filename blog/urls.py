from django.urls import path
# pyrefly: ignore [missing-import]
from . import views

urlpatterns = [
    # 1. Main Blog Feed Index Layout Home
    path('', views.index, name='blogHome'),

    # 2. Dynamic Single Post Viewer Path (Matches e.g. /blog/blogpost/1/)
    path('blogpost/<int:post_id>/', views.blogpost, name='blogpost'),
    
    # 3. FIXED: Catch-all fallback route when the user leaves off the numeric ID number
    # (Matches exactly /blog/blogpost/ or /blog/blogpost)
    path('blogpost/', views.blogpost, name='blogpost_fallback'),
    path('postComment/', views.postComment, name='postComment'),
    path('deleteComment/<int:sno>/', views.deleteComment, name='deleteComment'),
    path('like/<int:post_id>/', views.likePost, name='like_post'),
]