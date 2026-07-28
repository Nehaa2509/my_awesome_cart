from django.db import models
from django.contrib.auth.models import User  
from django.utils.timezone import now        

# =========================================================================
# 1. Main Blog Post Structure Table (Merged into ONE clean declaration)
# =========================================================================
class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default="General")
    chead = models.CharField(max_length=500, default="")
    author = models.CharField(max_length=100, default="")
    content = models.CharField(max_length=5000, default="")
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to="blog/images", default="")
    
    # Track user likes using an explicit string model reference to prevent schema collisions
    likes = models.ManyToManyField('auth.User', blank=True, related_name='blog_likes')

    def __str__(self):
        return self.title
        
    def total_likes(self):
        return self.likes.count()

    @property
    def subheading(self):
        return self.chead


# =========================================================================
# 2. Native Comments Management Table
# =========================================================================
class BlogComment(models.Model):
    sno = models.AutoField(primary_key=True)
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 🔗 Links the comment securely to a specific post ID
    post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title[:20]}..."