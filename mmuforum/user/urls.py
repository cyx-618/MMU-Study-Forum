from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from user import views as user_views

#URLconf

#urlpatterns = [
#path('_urlname_',views._functionname_)
#]
#写完之后去urls.py(main)

urlpatterns = [
    path('signup/', views.signup, name='forum-signup-user'),
    path('login/', views.login, name='forum-login-user'),
    path('profile/', views.profile, name= 'forum-profile'),
    path('feedback/', views.submit_feedback, name='submit-feedback'),
    path('feedback/list/', views.feedback_list, name='feedback-list'),
    path('profile/<str:username>/', views.view_profile, name='view-profile'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('delete-profile/', views.delete_profile, name='delete-profile'),
    path('notifications/', views.notifications, name='user-notifications'),
    path('feedback/<int:feedback_id>/', views.feedback_detail, name='feedback-detail'),
    path('views-other-profile/<int:user_id>/', views.view_other_profile, name='view-other-profile'),
    path('forgot-password/', views.forgot_password_view, name='forgot-password'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('resend-otp/', views.resend_otp_view, name='resend-otp'),
    path('view-report',views.view_report,name='view-report'),
    path('sign-up-verify',views.sign_up_verify,name='sign-up-verify'),
    
]