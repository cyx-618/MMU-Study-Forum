from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from post.models import Post, Comment, Like
from user.models import User, User_profile, Major
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password

# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def admin_main(request):
    posts = Post.objects.all().order_by('-date_posted')

    context = {
        'posts': posts,
    }
    return render(request, 'admin_manager/admin_main.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_post_detail(request, post_id):
    post=get_object_or_404 (Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'admin_manager/admin_post_detail.html', context)

@user_passes_test(lambda u: u.is_superuser)
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.likes_count.filter(id=request.user.id).exists():
        comment.likes_count.remove(request.user)
        liked = False
    else:
        comment.likes_count.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked, 
        'count': comment.likes_count.count()
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    return render(request, 'admin_manager/admin_panel.html')


@user_passes_test(lambda u: u.is_superuser)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_manager/admin_user_management.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def delete_user_confirmation(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'admin_manager/admin_um_delete_user.html', {'user': user})


@user_passes_test(lambda u: u.is_superuser)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        user.delete()
    return redirect('user-management')


@user_passes_test(lambda u: u.is_superuser)
def add_user(request):
    majors = Major.objects.all().order_by('major_name')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        is_staff = request.POST.get('is_staff') == 'True'
        major_id = request.POST.get('major')

        if not username:
            messages.error(request, 'Username is required.')
            return redirect('add-user')
        
        if not password or not password_confirm:
            messages.error(request, 'Password and password confirmation is required.')
            return redirect('add-user')
        
        if not major_id:
            messages.error(request, 'Major is required.')
            return redirect('add-user')

        if password != password_confirm:
            messages.error(request, 'Password and password confirmation not matched.')
            return redirect('add-user')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already in used.')
            return redirect('add-user')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in used.')
            return redirect('add-user')
        
        try:
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                is_staff=is_staff,
            )

            major = None
            if major_id:
                major = Major.objects.filter(id=major_id).first()
            
            User_profile.objects.create(
                user=user,
                major=major,
            )

            messages.success(request, f'User "{username}" has been successfully created.')
            return redirect('user-management')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return redirect('add-user')
        
    return render(request, 'admin_manager/admin_um_add_user.html', {'majors': majors})


@user_passes_test(lambda u: u.is_superuser)
def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = User_profile.objects.filter(user=user).first()
    posts = Post.objects.filter(author=user).order_by('-date_posted')
    post_count = posts.count()
    liked_posts = Post.objects.filter(likes__user=user).order_by('-date_posted')
    
    context = {
        'profile_user': user,
        'user_profile': user_profile,
        'posts': posts,
        'post_count': post_count,
        'liked_posts': liked_posts,
    }
    return render(request, 'admin_manager/admin_view_profile.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_profile(request):
    user= request.user
    posts= Post.objects.filter(author=user).order_by('-date_posted')
    post_count = posts.count()
    liked_posts = Post.objects.filter(likes__user=user).order_by('-date_posted')
    
    context = {
        'profile_user': user,
        'posts': posts,
        'post_count': post_count,
        'liked_posts': liked_posts,
    }
    return render(request, 'admin_manager/admin_view_profile.html', context)


@user_passes_test(lambda u: u.is_superuser)
def edit_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    user_profile = User_profile.objects.filter(user=target_user).first()
    majors = Major.objects.all().order_by('major_name')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        major_id = request.POST.get('major')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        password = request.POST.get('password')
        profile_picture = request.FILES.get('profile_picture')

        if not username:
            messages.error(request, 'Username is required.')
            return redirect('admin-edit-user-profile', user_id=user_id)
        
        if User.objects.exclude(id=target_user.id).filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('admin-edit-user-profile', user_id=user_id)
        
        target_user.username = username
        target_user.is_active = is_active
        target_user.is_staff = is_staff

        if password:
            target_user.password = password
        target_user.save()

        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.bio = bio
        if major_id:
            user_profile.major = Major.objects.filter(id=major_id).first()
        else:
            user_profile.major = None
        user_profile.save()
        
        messages.success(request, f'User "{username}" profile updated successfully.')
        return redirect('user-management')
    
    context = {
        'profile_user': target_user,
        'user_profile': user_profile,
        'majors': majors,
    }
    return render(request, 'admin_manager/admin_um_edit_user.html', context)


@user_passes_test(lambda u: u.is_superuser)
def batch_delete_confirmation(request):
    ids_str = request.GET.get('ids', '')
    if not ids_str:
        return redirect('user-management')
    
    user_ids = [int(id) for id in ids_str.split(',')]
    users = User.objects.filter(id__in=user_ids)

    return render(request, 'admin_manager/admin_um_delete_user.html', {'users': users, 'is_batch': True})


@user_passes_test(lambda u: u.is_superuser)
def batch_delete_execute(request):
    if request.method == 'POST':
        ids_str = request.POST.get('ids', '')
        if ids_str:
            user_ids = [int(id) for id in ids_str.split(',')]
            
            if request.user.id in user_ids:
                messages.error(request, 'You cannot delete yourself.')
                return redirect('user-management')
            
            count = User.objects.filter(id__in=user_ids).count()
            User.objects.filter(id__in=user_ids).delete()
            messages.success(request, f'Successfully deleted {count} user(s).')
        else:
            messages.error(request, 'No users selected.')
    
    return redirect('user-management')