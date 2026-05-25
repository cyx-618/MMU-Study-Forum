from django.shortcuts import redirect
from django.urls import reverse

class MajorRequirementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_has_major= False
            if hasattr(request.user, 'user_profile') and request.user.user_profile.major:
                user_has_major = True

            allowed_urls = [
                reverse('forum-profile'),
                reverse('forum-login'),
                reverse('forum-logout'),
                reverse('forum-home')
            ]

            if not user_has_major and request.path not in allowed_urls and not request.path.startswith('/admin/'):
                return redirect('forum-profile')
            
        response = self.get_response(request)
        return response