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
    path('signup/', views.signup, name= 'forum-signup'),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='forum-login'),
    path('profile/', views.profile, name= 'forum-profile'),
    path('feedback/', views.submit_feedback, name='submit-feedback'),
    path('feedback/list/', views.feedback_list, name='feedback-list'),
    path('profile/<str:username>/', views.view_profile, name='view-profile'),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('delete-profile/', views.delete_profile, name='delete-profile'),
]