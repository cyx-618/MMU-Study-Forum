from django.shortcuts import render, redirect
#from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
# Create your views here.

#view function

#html名看他们的来改，先写一个

def signup (request):
    context = {
        'title':'Sign Up',
    }

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email')

            if not email or not email.endwith('@student.mmu.edu.my'):
                messages.error(request, 'Please enter a valid MMU student email address.')
                return render(request, 'user/signup.html', {'form': form})
            
            user = form.save(commit=False)
            user.email = email
            user.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully! Welcome, {username}!')
            return redirect('forum-main')
        
    else:
        form = UserCreationForm()
    return render(request, 'user/signup.html', {'form': form})


def login (request):
    context = {
        'title':'Log In',
    }

    form = UserCreationForm()
    return render(request, 'user/signup.html', {'form': form})
