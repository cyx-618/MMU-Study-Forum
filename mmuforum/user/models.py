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
