from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='forum-main'),
]

urlpatterns = [
    path('', views.main_page, name='forum-main'),
    path('create-post/', views.create_post_page, name='create-post'),
]