from django.contrib import admin
from .models import Post, Category, Post_status 

# Register your models here.
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Post_status)