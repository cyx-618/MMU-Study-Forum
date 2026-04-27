from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='forum-home')
def main(request):
    return render(request, 'post/main.html',{'username': request.user.username})

@login_required(login_url='forum-home')
def create_post_page(request):
    return render(request, 'post/create-post.html')
