from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# pyrefly: ignore [missing-import]
from .models import BlogPost, BlogComment

def index(request):
    # 1. Fetch the active category parameter from the URL query string
    selected_category = request.GET.get('category', '').strip()
    
    # 2. Get all distinct categories currently in the database to keep the nav dynamic
    all_categories = BlogPost.objects.values_list('category', flat=True).distinct()
    
    # 3. Filter posts if a specific category is selected; otherwise, fetch all
    if selected_category:
        myposts = BlogPost.objects.filter(category__iexact=selected_category).order_by('-pub_date')
    else:
        myposts = BlogPost.objects.all().order_by('-pub_date')
        
    params = {
        'myposts': myposts,
        'posts': myposts,
        'all_categories': all_categories,
        'selected_category': selected_category
    }
    return render(request, 'blog/index.html', params)

def blogpost(request, post_id=None, id=None):
    target_id = post_id if post_id is not None else id
    if target_id is None:
        return redirect('/blog/')

    # 1. Fetch the targeted blog article post record safely
    post = BlogPost.objects.filter(post_id=target_id).first()
    
    if not post:
        return redirect('/blog/') # Clean error fallback logic

    # 2. Intercept comment form submission tracking vectors
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to leave a comment.")
            return redirect(f'/blog/blogpost/{target_id}/')
            
        comment_content = request.POST.get('comment', '').strip()
        
        if comment_content:
            # Create and save the new comment model instances directly
            new_comment = BlogComment(
                comment=comment_content, 
                user=request.user, 
                post=post
            )
            new_comment.save()
            messages.success(request, "Your comment has been posted successfully!")
        else:
            messages.error(request, "Comment body content cannot be empty.")
            
        return redirect(f'/blog/blogpost/{target_id}/')

    # 3. Gather all comments attached to this specific post to display them
    comments = post.comments.all().order_by('-timestamp')
    
    params = {
        'post': post, 
        'comments': comments
    }
    return render(request, 'blog/blogpost.html', params)

def postComment(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a comment.")
            return redirect('/blog/')
            
        comment = request.POST.get("comment", "").strip()
        postSno = request.POST.get("postSno")
        
        if comment and postSno:
            post = get_object_or_404(BlogPost, post_id=postSno)
            new_comment = BlogComment(comment=comment, user=request.user, post=post)
            new_comment.save()
            messages.success(request, "Your comment has been posted successfully!")
            return redirect(f"/blog/blogpost/{post.post_id}/")
        else:
            messages.error(request, "Comment body content cannot be empty.")
            
    return redirect('/blog/')

def deleteComment(request, sno):
    if request.user.is_authenticated:
        comment = get_object_or_404(BlogComment, sno=sno)
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
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        
    return redirect(f"/blog/blogpost/{post_id}/")