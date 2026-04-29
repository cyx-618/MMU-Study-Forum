from django.urls import path
from .views import (
    PostListView, 
    PostCreateView 
    #,PostDetailView
)
from . import views

urlpatterns = [
    path('main/', views.main, name='forum-main'),
    path('create-post/', views.create_post_page, name='create-post'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='forum-main'),
    path('forum/<str:major_name>/', views.major_post_list, name='major-forum'),
    #path('post/<int:pk>/', PostDetailView.as_view(), name='forum-post-detail'),
]

#<app>/<model>_<viewtype>.html
