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
    is_reported = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_posts')

    is_announcement = models.BooleanField(default=False)
    pinned_until = models.DateTimeField(null=True, blank=True)

    def is_pinned(self):
        if not self.pinned_until:
            return False
        return self.is_announcement and timezone.now() < self.pinned_until

    def total_likes(self):
        return self.likes.count()

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
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_comments')

    class Meta:
        verbose_name_plural = 'Comments'


    def total_likes(self):
        return self.likes_count.count()
    
    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"
    
class ReportPost(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
    ]

    RESOLUTION_CHOICES = [
        ('approved_deleted', 'Approved - Content Deleted'),
        ('aproved_warned', 'Approved - User Warned'),
        ('approved_suspended', 'Approved - User Suspended'),
        ('dismissed', 'Dismissed - No Action'),
    ]
    
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    resolution = models.CharField(max_length=50, choices= RESOLUTION_CHOICES, blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['post', 'reporter']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reporter.username} reported {self.post.title} for {self.reason}"
    
class ReportComment(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('hate_speech', 'Hate Speech'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
    ]

    RESOLUTION_CHOICES = [
        ('approved_deleted', 'Approved - Comment Deleted'),
        ('approved_warned', 'Approved - User Warned'),
        ('approved_suspended', 'Approved - User Suspended'),
        ('dismissed', 'Dismissed - No Action'),
    ]
    
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='comment_reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    resolution = models.CharField(max_length=50, choices= RESOLUTION_CHOICES, blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['comment', 'reporter']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reporter.username} reported {self.comment.id} for {self.reason}"

