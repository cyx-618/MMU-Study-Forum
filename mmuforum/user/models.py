from django.db import models

# Create your models here.

class Major (models.Model):
    major_name = models.CharField(max_length=45)

