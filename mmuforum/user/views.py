from multiprocessing import context
from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout
from .models import Notification, User_profile, Feedback
from post.models import Like, Post
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .form import (
    UserRegisterForm,
    UserUpdateForm,
    FeedbackForm,
    LoginForm,
)

#view function

def signup (request):
    context = {
        'title':'Sign Up',
    }

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')

            if not email or not email.endswith('@student.mmu.edu.my'):
                messages.error(request, 'Please enter a valid MMU student email address.')
                return render(request, 'user/signup.html', {'form': form})
            
            user = form.save(commit=False)
            user.email = email
            user.save()

            User_profile.objects.get_or_create(user=user)

            auth_login(request, user)

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('forum-profile')
        
    else:
        form = UserRegisterForm()
    return render(request, 'user/signup.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dispatch-user')
    else:
        form= LoginForm(request=request)

    context = {
        'title': 'Log In',
        'form': form,
    }

    return render(request, 'user/login.html',context)


def dispatch_user(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('admin-main')
    else:
        return redirect('forum-main')


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user.user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('forum-main')
    else:
        form = UserUpdateForm(instance=request.user.user_profile)
    
    context={
        'title':'Update Profile'
    }
    return render(request,'user/profile.html',{'form': form})


@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()

            Notification.objects.create(
                receiver=request.user,
                sender=request.user,
                notification_type='feedback_submitted',
                feedback=feedback,
                post=None
            )

            #send email
            admin_and_staff = User.objects.filter(
                Q(is_superuser=True) | Q(is_staff=True)
            ).distinct()

            recipient_list = [u.email for u in admin_and_staff if u.email]

            for admin_user in admin_and_staff:
                Notification.objects.create(
                    receiver=admin_user,
                    sender=request.user,
                    notification_type='new_feedback',
                    feedback=feedback,
                    post=None
                )

            if recipient_list:
                feedback_subject = form.cleaned_data.get('subject', 'No Subject.')
                feedback_message = form.cleaned_data.get('message', 'No message.')
                email_body = f"""Hi Admin, Staff or Superuser,

A new feedback has been submitted by {request.user.username}. Remember to reply them.
Email: {request.user.email}
Subject: {feedback_subject}
Message: {feedback_message}

From MMU Forum Admin System
                """            
                try:
                    send_mail(
                        subject = f'New Feedback from {request.user.username}',
                        message = email_body,
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = recipient_list,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

            messages.success(request, 'Your feedback has been submitted!')
            return redirect('feedback-list')
    
    else:
        form = FeedbackForm()

    context = {
        'title': 'Submit Feedback'
    }
    return render(request, 'user/feedback.html', {'form': form})


@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'feedbacks': feedbacks,
        'title': 'My Feedback'
    }
    return render(request, 'user/feedback_list.html', context)


@login_required
def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if not request.user.is_superuser and not request.user.is_staff and feedback.user != request.user:
        messages.error(request, 'You do not have permission to view this feedback.')
        return redirect('forum-list')
    
    context = {
        'feedback': feedback,
        'title': f'Feedback Detail - {feedback.subject}'
    }

    return render(request, 'user/feedback_detail.html', context)


@login_required
def view_profile(request,username):
    user=get_object_or_404(User, username=username)
    user_profile = User_profile.objects.filter(user=user).first()
    posts = Post.objects.filter(author=user).order_by('-date_posted')
    post_count = posts.count()
    liked_posts = Post.objects.filter(likes__user=user).order_by('-date_posted')

  
    if request.user.is_authenticated:
        user_post_count = Post.objects.filter(author=request.user).count()
    else:
        user_post_count = 0
    context = {
        'profile_user': user,
        'user_profile': user_profile,
        'posts': posts,
        'post_count': post_count,
        'liked_posts': liked_posts,
    }
    return render(request, 'user/view_profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user.user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('view-profile', username=request.user.username)
    else:
        form = UserUpdateForm(instance=request.user.user_profile)
    
    context={
        'title':'Edit Profile',
        'form': form,
    }
    return render(request,'user/edit_profile.html',{'form': form})


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted!')
        return redirect('forum-home')
    return render(request, 'user/delete_profile.html')


@login_required
def notifications(request):
    notifications = request.user.notifications.all()

    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    return render(request, 'user/notification.html', {'notifications': notifications})
    

@login_required
def view_other_profile(request,user_id):
    profile_user = get_object_or_404(User, id=user_id)

    if not profile_user.user_profile:
        messages.error(request, 'User not found.')
        return redirect('forum-main')

    user_posts = Post.objects.filter(author=profile_user).order_by('-date_posted')
    user_posts_count = user_posts.count()

    context = {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'user_posts_count': user_posts_count,
        'user': profile_user,
        'title': f"{profile_user.username}'s Profile"
    }
    return render(request, 'user/view_other_profile.html', context)

