from django.urls import path
from . import views

urlpatterns = [
    path('admin/main', views.admin_main, name='admin-main'),
    path('admin/post/<int:post_id>/', views.admin_post_detail, name='admin-post-detail'),
    path('admin/like-comment/<int:comment_id>/', views.like_comment, name='like_comment'),
]