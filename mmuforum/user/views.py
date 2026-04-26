from django.shortcuts import render, redirect
#from django.http import HttpResponse
from django.contrib import messages
from .form import UserRegisterForm
from .form import UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
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

            from .models import User_profile
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
