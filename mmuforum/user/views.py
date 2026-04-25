from django.shortcuts import render, redirect
#from django.http import HttpResponse
from django.contrib import messages
from .form import UserRegisterForm
from .form import UserUpdateForm
from .form import UserFeedbackForm
from .models import Feedback
from django.contrib.auth.decorators import login_required
# Create your views here.

#view function

#html名看他们的来改，先写一个

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

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('forum-main')
        
    else:
        form = UserRegisterForm()
    return render(request, 'user/signup.html', {'form': form})
#----------------------------------------------------------------------------------------------------------

def login (request):
    context = {
        'title':'Log In',
    }

    form = UserRegisterForm()
    return render(request, 'user/signup.html', {'form': form})

#----------------------------------------------------------------------------------------------------------

def profile(request):
    form=UserUpdateForm()
    context={
        'title':'Update Profile'
             }
    return render(request,'user/profile.html',{'form': form})
  #havent finish the profile update form, have to link to mainpage and the profile function

#----------------------------------------------------------------------------------------------------------

@login_required
def feedback_view(request):
   user_reports = Feedback.objects.filter(user=request.user).order_by('-date_submitted')
  
   if request.method == 'POST':
        form = UserFeedbackForm(request.POST)
        if form.is_valid():
            new_report = form.save(commit=False)
            new_report.user = request.user 
            new_report.save()
            return redirect('feedback_view') 
   else:
        form = UserFeedbackForm()

   return render(request, 'user/feedback.html', {
        'form': form,
        'user_reports': user_reports,
       

    })

#----------------------------------------------------------------------------------------------------------