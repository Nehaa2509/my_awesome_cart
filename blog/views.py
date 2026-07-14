from django.shortcuts import render, get_object_or_404, redirect
from .models import Blogpost  # <-- Change BlogPost to your actual class name here!

def index(request):
    posts = Blogpost.objects.all().order_by('-pub_date')  # <-- Update class name here too
    return render(request, 'blog/index.html', {'posts': posts})

def blogpost(request, post_id=None):
    if post_id is None:
        return redirect('/blog/')
    post = get_object_or_404(Blogpost, post_id=post_id)  # <-- Update class name here too
    return render(request, 'blog/blogpost.html', {'post': post})