from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import BlogPost, BlogComment  # FIXED: Cleaned up duplicate/incorrect class imports

def index(request):
    # FIXED: Updated to BlogPost matching your models configuration
    posts = BlogPost.objects.all().order_by('-pub_date')  
    return render(request, 'blog/index.html', {'posts': posts})

def blogpost(request, post_id=None):
    if post_id is None:
        return redirect('/blog/')
    # FIXED: Updated to BlogPost matching your models configuration
    post = get_object_or_404(BlogPost, post_id=post_id)  
    return render(request, 'blog/blogpost.html', {'post': post})

def postComment(request):
    if request.method == "POST":
        # SAFETY CHECK: If a user isn't logged in, redirect them back gently
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a comment.")
            return redirect('/blog/')
            
        comment = request.POST.get("comment")
        postSno = request.POST.get("postSno")
        
        # FIXED: Updated to look up the correct BlogPost instance structure
        post = get_object_or_404(BlogPost, post_id=postSno)
        user = request.user
        
        # Save the new comment record row
        new_comment = BlogComment(comment=comment, user=user, post=post)
        new_comment.save()
        messages.success(request, "Your comment has been posted successfully!")
        
        return redirect(f"/blog/blogpost/{post.post_id}/")
        
    return redirect('/blog/')

def deleteComment(request, sno):
    if request.user.is_authenticated:
        # Fetch the comment safely using its primary key serialization index
        comment = get_object_or_404(BlogComment, sno=sno)
        
        # Security Check: Only allow the author or an admin to delete it
        if comment.user == request.user or request.user.is_staff:
            post_id = comment.post.post_id
            comment.delete()
            messages.success(request, "Comment deleted successfully!")
            return redirect(f"/blog/blogpost/{post_id}/")
            
    messages.error(request, "You are not authorized to delete this comment.")
    return redirect('/blog/')

def likePost(request, post_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like posts.")
        return redirect(f"/blog/blogpost/{post_id}/")
        
    post = get_object_or_404(BlogPost, post_id=post_id)
    
    # Toggle logic: If liked already -> remove like. If not -> add like.
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        
    return redirect(f"/blog/blogpost/{post_id}/")