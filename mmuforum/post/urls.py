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
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add-comment'),
    path('report/<int:post_id>/', views.report_post, name='report-post'),
]

#<app>/<model>_<viewtype>.html