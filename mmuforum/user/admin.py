from django.contrib import admin
from .models import Feedback
# Register your models here.

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'date_submitted', 'is_resolved')
    readonly_fields =('user', 'subject', 'message', 'date_submitted')