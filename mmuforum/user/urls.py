from django.urls import path
from . import views

#URLconf

#urlpatterns = [
#path('_urlname_',views._functionname_)
#]
#写完之后去urls.py(main)

urlpatterns = [
    path('signup/', views.signup, name='forum-signup'),
    path('login/', views.login, name='forum-login')
]