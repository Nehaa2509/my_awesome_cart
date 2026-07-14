from django.db import models

# Create your models here.
class Blogpost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    chead = models.CharField(max_length=500, default="")
    author = models.CharField(max_length=100, default="")
    content = models.CharField(max_length=5000, default="")
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to="blog/images", default="")

    def __str__(self):
        return self.title
