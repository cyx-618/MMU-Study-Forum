from django.db import models

# Create your models here.

class Account (models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    email = models.EmailField(max_length=35)

    def __str__(self):
        return f"{self.username} ({self.email})"
class Major (models.Model):
    major_name = models.CharField(max_length=45)

class User_profile (models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    major = models.ForeignKey(Major, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

