from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Major (models.Model):
    major_name = models.CharField(max_length=45)
    class Meta:
        verbose_name_plural = 'Majors'

    def __str__(self):
        return self.major_name

class User_profile (models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_picture/', default='profile_picture/default.png', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=1000)
    admin_reply = models.TextField(max_length=1000, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username}: {self.subject}"


class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')

    TYPE_CHOICES = (
        ('post_like', 'liked your post'),
        ('post_comment', 'commented on your post'),
        ('comment_reply', 'replied to your comment'),
        ('comment_like', 'liked your comment'),
        ('admin_reply', 'replied to your feedback'),
        ('feedback_submitted', 'You have submitted a feedback.'),
    )

    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, null=True, blank=True)
    feedback = models.ForeignKey('user.Feedback', on_delete=models.CASCADE, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        action = self.get_notification_type_display()
        return f"{self.sender.username} {action} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
