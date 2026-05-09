from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse

# Create your models here.

class Category (models.Model):
    category = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category

class Post (models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField(max_length=2000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)

    pdf = models.FileField(upload_to='post_pdfs/', null=True, blank=True)
    video_file = models.FileField(upload_to='post_videos/', null=True, blank=True)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Posts'

    def __str__(self):
        return self.title
    
    #def get_absolute_url(self):
        #return reverse('post-detail', kwargs={'pk': self.pk} )

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'post']
    
class Comment (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=300)
    created_at = models.DateTimeField(default=timezone.now)

    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    likes_count = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)
    dislikes_count = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_dislikes', blank=True)

    class Meta:
        verbose_name_plural = 'Comments'

    def total_likes(self):
        return self.likes_count.count()
    
    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"