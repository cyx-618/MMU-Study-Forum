import random
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta


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
        
        ('report_approved', 'Report Approved'),
        ('report_dismissed', 'Report Dismissed'),
        ('content_warning', 'Content Warning'),
        ('content_deleted', 'Content Deleted'),
        ('account_suspended', 'Account Suspended'),

        ('new_feedback', 'submitted a new feedback'),
        ('new_report', 'submitted a new report'),
    )

    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    post = models.ForeignKey('post.Post', on_delete=models.CASCADE, null=True, blank=True)
    feedback = models.ForeignKey('user.Feedback', on_delete=models.CASCADE, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        action = self.get_notification_type_display()
        return f"{self.sender.username} {action} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_message(self):
        if self.notification_type == 'post_like':
            return f"{self.sender.username} liked your post"
        elif self.notification_type == 'post_comment':
            return f"{self.sender.username} commented on your post"
        elif self.notification_type == 'comment_reply':
            return f"{self.sender.username} replied to your comment"
        elif self.notification_type == 'comment_like':
            return f"{self.sender.username} liked your comment"
        elif self.notification_type == 'admin_reply':
            return f"Admin replied to your feedback"
        elif self.notification_type == 'feedback_submitted':
            return f"You have submitted a feedback"
        elif self.notification_type == 'report_approved':
            return f"Your report has been approved. The content has been removed."
        elif self.notification_type == 'report_dismissed':
            return f"Your report has been reviewed and dismissed."
        elif self.notification_type == 'content_warning':
            return f"You have received a warning for violating community guidelines."
        elif self.notification_type == 'content_deleted':
            return f"Your content has been removed for violating guidelines."
        elif self.notification_type == 'account_suspended':
            return f"Your account has been suspended for violating guidelines."
        elif self.notification_type == 'new_feedback':
            return f"{self.sender.username} submitted a new feedback."
        elif self.notification_type == 'new_report':
            return f"{self.sender.username} submitted a new report for post."
        return "You have a new notification"

class ProfileOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # OTP is valid for 10 minutes
        return timezone.now() < self.created_at + timedelta(minutes=10)

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.created_at = timezone.now()
        self.save()