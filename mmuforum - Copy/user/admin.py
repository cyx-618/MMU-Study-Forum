from django.contrib import admin
from .models import Feedback, Major, User_profile

# Register your models here.

admin.site.register(Major)
admin.site.register(User_profile)
admin.site.register(Feedback)



