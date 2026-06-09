from django.urls import path
from . import views

urlpatterns = [
    path('admin/main', views.admin_main, name='admin-main'),
    path('admin/post/<int:post_id>/', views.admin_post_detail, name='admin-post-detail'),
    path('admin/like-comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('admin/panel/', views.admin_panel, name='admin-panel'),
    path('admin/panel/user-management/', views.user_management, name='user-management'),
    path('admin/panel/user-management/edit/<int:user_id>/', views.edit_user, name='edit-user'),
    path('admin/panel/user-management/delete/<int:user_id>/', views.delete_user_confirmation, name='delete-user-confirmation'),
    path('admin/panel/user-management/delete/execute/<int:user_id>/', views.user_delete, name='delete-user-execute'),
    path('admin/panel/user-management/adduser/', views.add_user, name='add-user'),
    path('admin/profile/<int:user_id>', views.view_profile, name='view-profile'),
    path('admin/profile/my', views.admin_profile, name='my-profile'),
    path('admin/panel/user-management/delete/batch-confirm/', views.batch_delete_confirmation, name='batch-delete-confirmation'),
    path('admin/panel/user-management/delete/batch-execute/', views.batch_delete_execute, name='batch-delete-execute'),
]