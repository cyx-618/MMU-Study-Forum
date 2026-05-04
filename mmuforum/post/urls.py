from django.urls import path
from .views import (
    PostListView, 
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostDetailView
)
from . import views

urlpatterns = [
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('', PostListView.as_view(), name='forum-main'),
    path('forum/<str:major_name>/', views.major_post_list, name='major-forum'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]

#<app>/<model>_<viewtype>.html