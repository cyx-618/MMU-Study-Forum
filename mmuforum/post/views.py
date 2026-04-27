from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
<<<<<<< HEAD
from django.contrib.auth.decorators import login_required
=======
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import (
    ListView, 
    #DetailView, 
    CreateView, 
    #UpdateView, 
    #DeleteView
    )
from post.models import Post
from user.models import Feedback
>>>>>>> 268d7f1887433072097b5bdbb38139a7525007b0

# Create your views here.
@login_required(login_url='forum-home')
def main(request):
<<<<<<< HEAD
    return render(request, 'post/main.html',{'username': request.user.username})

@login_required(login_url='forum-home')
def create_post_page(request):
    return render(request, 'post/create-post.html')
=======
    context = {
        'posts': Post.objects.all(),
        'title':'Main Forum',
    }
    return render(request, 'post/dummy_main.html', context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'category','image']
    template_name = 'post/post_form.html' #change to create-post.html
    success_url = '/main/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
def major_post_list(request, major_name):
        posts = Post.objects.filter(author__user_profile__major__major_name=major_name).order_by('-date_posted')

        context = {
            'posts': posts,
            'major_name': major_name,
            'title': f'{major_name} Forum'
        }
        return render(request, 'post/major_forum.html', {'posts': posts, 'major_name': major_name})

class  PostListView(ListView):
    model = Post
    template_name = 'post/dummy_main.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']




#class PostDetailView(DetailView):
    #model = Post
>>>>>>> 268d7f1887433072097b5bdbb38139a7525007b0
