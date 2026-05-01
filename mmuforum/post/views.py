from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    UserPassesTestMixin
)
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView
    )
from post.models import Post
from user.models import Feedback

# Create your views here.
def main(request):
    context = {
        'posts': Post.objects.all(),
        'title':'Main Forum',
    }
    return render(request, 'post/main.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'category','image']
    template_name = 'post/create_post.html'
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
    template_name = 'post/main.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']


class PostDetailView(DetailView):
    model = Post
    template_name = 'post/detail_post.html'


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category','image']
    template_name = 'post/update_post.html' 
    success_url = '/main/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or self.request.user.is_superuser:
            return True
        return False
    
    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'post/delete_post.html' 
    success_url = '/main/'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    