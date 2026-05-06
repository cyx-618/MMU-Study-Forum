from django.shortcuts import get_object_or_404, render, redirect
#from django.http import HttpResponse
from django.contrib import messages
from .form import (
    UserRegisterForm,
    UserUpdateForm,
    FeedbackForm
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout
from .models import User_profile, Feedback
from post.models import Post
# Create your views here.

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

def login (request):
    context = {
        'title':'Log In',
    }

    form = UserRegisterForm()
    return render(request, 'user/signup.html', {'form': form})


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
def view_profile(request, username):
    user_profile = User_profile.objects.filter(user__username=username).first()
    user_posts = Post.objects.filter(author=user_profile.user).order_by('-date_posted')
    
    context = {
        'view_profile': user_profile,
        'user_posts': user_posts,
        'user': user_profile.user,
        'title': f"{user_profile.user.username}'s Profile"
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


def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted!')
        return redirect('forum-home')
    return render(request, 'user/delete_profile.html')