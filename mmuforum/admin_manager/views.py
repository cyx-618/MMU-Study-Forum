from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from post.models import Post, Comment, Like, ReportComment, ReportPost, Category
from user.models import User, User_profile, Major, Feedback, Notification, Major
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout


# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def admin_main(request):
    query = request.GET.get('q')
    search_type = request.GET.get('type', 'post')
    posts = Post.objects.all().order_by('-is_announcement', '-date_posted')

    if query:
        if search_type == 'post':
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
        elif search_type == 'user':
            posts = posts.filter(author__username__icontains=query)

    for post in posts:
        post.user_has_liked = Like.objects.filter(post=post, user=request.user).exists()

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
def admin_like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    existing_like = Like.objects.filter(post=post, user=request.user).first()
    
    if existing_like:
        existing_like.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True

    total_likes = Like.objects.filter(post=post).count()

    return JsonResponse({
        'liked': liked,
        'count': total_likes
    })

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
    query = request.GET.get('q')
    search_type = request.GET.get('type', 'username')
    users = User.objects.all().order_by('-date_joined')

    if query:
        if search_type == 'username':
            users = users.filter(username__icontains=query)
        elif search_type == 'email':
            users = users.filter(email__icontains=query)
        elif search_type == 'major':
            users = users.filter(user_profile__major__major_name__icontains=query)

    context = {
        'users': users,
        'query': query,
        'search_type': search_type,
    }
    return render(request, 'admin_manager/admin_user_management.html', context)


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


@user_passes_test(lambda u: u.is_superuser)
def feedback_center(request):
    query = request.GET.get('q')
    feedbacks = Feedback.objects.all().order_by('-created_at')

    if query:
        feedbacks = feedbacks.filter(
            Q(subject__icontains=query) |
            Q(message__icontains=query)
        )

    context = {
        'feedbacks': feedbacks,
        'query': query
    }

    return render(request, 'admin_manager/admin_feedback_center.html', context)


@user_passes_test(lambda u: u.is_superuser)
def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)

    if request.method == 'POST':
        feedback.admin_reply = request.POST.get('admin_reply')
        feedback.is_resolved = request.POST.get('is_resolved') == 'on'
        feedback.save()

        Notification.objects.create(
            receiver=feedback.user,
            sender=request.user,
            notification_type='admin_reply',
            feedback=feedback,
            post=None
        )

        if feedback.is_resolved and feedback.user.email:
            subject = f"Admin reply to your Feedback: {feedback.subject}"
            email_body = f"""
Hi {feedback.user.username},

Admin has reviewed your feedback.

Your feedback: {feedback.message}

Admin Reply: {feedback.admin_reply}

Status: {'Resolved' if feedback.is_resolved else 'Pending'}

From MMU Forum Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[feedback.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {e}")

        messages.success(request, 'Reply sent successfully.')
        return redirect('feedback-center')
    
    
    
    context = {
        'feedback': feedback
    }
    return render(request, 'admin_manager/admin_feedback_detail.html', context)


@user_passes_test(lambda u: u.is_superuser)
def report_center(request):
    query = request.GET.get('q')
    post_reports = ReportPost.objects.all().order_by('-created_at')
    comment_reports = ReportComment.objects.all().order_by('-created_at')

    if query:
        post_reports = post_reports.filter(reason__icontains=query)
        comment_reports = comment_reports.filter(reason__icontains=query)

    context= {
        'post_reports': post_reports,
        'comment_reports': comment_reports,
        'query': query
    }
    return render(request, 'admin_manager/admin_report_center.html', context)


@user_passes_test(lambda u: u.is_superuser)
def report_process(request, report_type, report_id):
    if report_type == 'post':
        report = get_object_or_404(ReportPost, id=report_id)
    else:
        report = get_object_or_404(ReportComment, id=report_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            if report_type == 'post':
                report.post.delete()
                offender = report.post.author
            else:
                report.comment.delete()
                offender = report.comment.user

            resolution = 'approved_deleted'
            reporter_msg = f'Your report has been approved. The {report_type} has been deleted.'
            offender_msg = f'Your {report_type} has been removed for violating guidelines.'
            offender_notification_type = 'content_deleted'

        elif action == 'warn':
            offender = report.post.author if report_type == 'post' else report.comment.user
            resolution = 'approved_warned'
            reporter_msg = f'Your report has been approved. The user has been warned.'
            offender_msg = f'You have received a warning for violating guidelines.'
            offender_notification_type = 'content_warning'

        elif action == 'suspend':
            offender = report.post.author if report_type == 'post' else report.comment.user
            offender.is_active = False
            offender.save()
            resolution = 'approved_suspended'
            reporter_msg = f'Your report has been approved. The user has been suspended.'
            offender_msg = f'Your account has been suspended for violating guidelines.'
            offender_notification_type = 'account_suspended'

        elif action == 'dismiss':
            resolution = 'dismissed'
            reporter_msg = f'Your report has been reviewed and dismissed as it does not violate guidelines.'
            offender_msg = None
            offender_notification_type = None
        
        else:
            messages.error(request, 'Invalid action.')
            return redirect('report-center')
        
        report.resolution = resolution
        report.resolved_at = timezone.now()
        report.status = 'reviewed'
        report.save()

        Notification.objects.create(
            receiver=report.reporter,
            sender=request.user,
            notification_type='report_approved' if resolution != 'dismissed' else 'report_dismissed',
            post= report.post if report_type == 'post' else None
        )

        if offender_msg:
            Notification.objects.create(
                receiver=offender,
                sender=request.user,
                notification_type=offender_notification_type,
                post=report.post if report_type == 'post' else None
            )

        if report.reporter.email:
            subject= f"Report Update: {report.post.title if report_type == 'post' else 'Comment Report'}"
            email_body= f"""
Hi {report.reporter},

The resolution for your report is 

{report.resolution}

From MMU Forum Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[report.reporter.email],
                    fail_silently=False,
                )

            except Exception as e:
                print(f"Error sending email to reporter: {e}")

        if offender_msg and offender.email:
            subject= f"Community Guidelines Violation"
            email_body= f"""
Hi {report.offender}

Your post/comment: {report.post.title if report_type == 'post' else ''} has violate the community rules.

We have already

{report.resolution}

Please do not violate the communitity rules again. We will take attention on your actions.

Thank you for using MMU Forum

From MMU Forum Team
"""
            try:
                send_mail(
                    subject=subject,
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[offender.email],
                    fail_silently=False,
                )

            except Exception as e:
                print(f"Error sending email to offender: {e}")
        
        messages.success(request, 'Report processed successfully.')
        return redirect('report-center')
    
    context = {
        'report': report,
        'report_type': report_type,
    }
    
    return render (request, 'admin_manager/admin_report_process.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'admin_manager/admin_notification.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_major(request, major_name):
    posts = Post.objects.filter(
        author__user_profile__major__major_name=major_name
    ).order_by('date_posted')

    for post in posts:
        post.user_has_liked = Like.objects.filter(post=post, user=request.user).exists()

    context = {
        'posts' : posts,
        'selected_major' : major_name,
    }
    return render(request, 'admin_manager/admin_main.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_database_management(request):
    majors = Major.objects.all().order_by('major_name')
    categories = Category.objects.all().order_by('category')

    context = {
        'majors' : majors,
        'categories': categories,
    }
    return render(request, 'admin_manager/admin_database_management.html', context)


@user_passes_test(lambda u: u.is_superuser)
def database_add(request, model_type):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(f"model_type: {model_type}")

        if name:
            if model_type == 'major':
                Major.objects.create(major_name=name)
            elif model_type == 'category':
                Category.objects.create(category=name)
            messages.success(request, f'{model_type.title()} added successfully.')
        else:
            messages.error(request, f'Name is required.')
        return redirect('database-management')
    
    context = {
        'model_type': model_type,
        'title': f'Add {model_type.title()}',
    }
    return render(request, 'admin_manager/admin_add_database.html', context)


@user_passes_test(lambda u: u.is_superuser)
def database_edit(request, model_type, item_id):
    if model_type == 'major':
        item = get_object_or_404(Major, id=item_id)
        field_value = item.major_name
    elif model_type == 'category':
        item = get_object_or_404(Category, id=item_id)
        field_value = item.category
    else:
        return redirect('database-management')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if model_type == 'major':
                item.major_name = name
            elif model_type == 'category':
                item.category = name
            item.save()
            messages.success(request, f'{model_type.title()} updated successfully.')
        else:
            messages.error(request, 'Name is required.')
        return redirect('database-management')
    
    context = {
        'item': item,
        'model_type': model_type,
        'title': f'{model_type.title()}',
        'field_value': field_value,
    }
    return render(request, 'admin_manager/admin_edit_database.html', context)


@user_passes_test(lambda u: u.is_superuser)
def database_delete_confirmation(request, model_type, item_id):
    if model_type == 'major':
        item = get_object_or_404(Major, id=item_id)
        item_name = item.major_name
    elif model_type == 'category':
        item = get_object_or_404(Category, id=item_id)
        item_name = item.category
    else:
        return redirect('database-management')
    
    context = {
        'item': item,
        'item_name': item_name,
        'model_type': model_type,
        'title': f'Delete {model_type.title()}',
    }
    return render(request, 'admin_manager/admin_delete_database.html', context)


@user_passes_test(lambda u: u.is_superuser)
def database_delete_execute(request, model_type, item_id):
    print(f"Deleting {model_type} with id {item_id}")
    if model_type == 'major':
        item = get_object_or_404(Major, id=item_id)
        item_name = item.major_name
    elif model_type == 'category':
        item = get_object_or_404(Category, id=item_id)
        item_name = item.category
    else:
        return redirect('database-management')
    
    item.delete()
    messages.success(request, f'{model_type.title()} "{item_name}" deleted successfully.')
    return redirect('database-management') 


def admin_logout(request):
    logout(request)
    return redirect('forum-home')


@user_passes_test(lambda u: u.is_superuser)
def admin_edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    categories = Category.objects.all().order_by('category')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        
        if title and content:
            post.title = title
            post.content = content
            
            if category_id:
                post.category = Category.objects.filter(id=category_id).first()
            else:
                post.category = None
            
            if 'image' in request.FILES:
                post.image = request.FILES['image']
            elif request.POST.get('delete_image') == 'on':
                post.image = None
                
            if 'video_file' in request.FILES:
                post.video_file = request.FILES['video_file']
            elif request.POST.get('delete_video') == 'on':
                post.video_file = None
            
            if 'pdf' in request.FILES:
                post.pdf = request.FILES['pdf']
            elif request.POST.get('delete_pdf') == 'on':
                post.pdf = None
            
            post.save()
            messages.success(request, 'Post updated successfully.')
            return redirect('admin-post-detail', post_id=post.id)
        else:
            messages.error(request, 'Title and content are required.')
    
    context = {
        'post': post,
        'categories': categories,
    }
    return render(request, 'admin_manager/admin_edit_post.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('admin-main')
    
    context = {
        'post': post,
    }
    return render(request, 'admin_manager/admin_delete_post.html', context)