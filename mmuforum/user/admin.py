from django.contrib import admin
from .models import Feedback, Major, User_profile, Notification
from django.core.mail import send_mail
from django.conf import settings

# Register your models here.

admin.site.register(Major)
admin.site.register(User_profile)
admin.site.register(Notification)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'message', 'is_resolved','created_at')
    list_filter = ('is_resolved', 'created_at')

    def save_model(self, request, obj, form, change):
        if change and obj.is_resolved and obj.admin_reply:
            notification_exists = Notification.objects.filter(
                receiver=obj.user,
                notification_type='admin_reply',
                feedback=obj
            ).exists()

            if not notification_exists:
                Notification.objects.create(
                    receiver=obj.user,
                    sender=request.user,
                    notification_type='admin_reply',
                    post=None,
                    feedback=obj
                    )
                
            subject = f"Update on your feedback: {obj.subject}"

            email_body = f"""
Hi {obj.user.username},
Our team has reviewed your feedback and replied to your feedback.

-----------------
Your Feedback:
"{obj.message}"

Admin's Response:
"{obj.admin_reply}"
-----------------

Status: This issue has been mark as resolved.

You can see the detail here: http://127.0.0.1:9000/user/feedback/list/

Thank you for be part of MMU Forum!
From MMU Forum Admin Team
            """

            try:
                send_mail(
                    subject,
                    email_body,
                    settings.EMAIL_HOST_USER,
                    [obj.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending reply email: {e}")

        super().save_model(request, obj, form, change)



