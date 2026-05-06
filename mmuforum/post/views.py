from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView, 
    UpdateView, 
    DeleteView
)
from post.models import Post, Like, Comment
from user.models import Feedback
from django.urls import reverse
from django.urls import reverse_lazy

# Create your views here.
def main(request):
    context = {
        'posts': Post.objects.all().prefetch_related('comments','likes'),
        'title':'Main Forum',
    }
    return render(request, 'post/main.html', context)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'category','image', 'pdf', 'video_file']
    template_name = 'post/create_post.html' #change to create_post.html
    success_url = reverse_lazy('forum-main')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


def major_post_list(request, major_name):
        posts = Post.objects.filter(author__user_profile__major__major_name=major_name).order_by('-date_posted').prefetch_related('comments','likes')

        context = {
            'posts': posts,
            'major_name': major_name,
            'title': f'{major_name} Forum'
        }
        #return render(request, 'post/major_forum.html', {'posts': posts, 'major_name': major_name})
        return render(request, 'post/major_forum.html', context)

class  PostListView(ListView):
    model = Post
    template_name = 'post/main.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']

#class PostDetailView(DetailView):
    #model = Post

#yj testing code
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        post.likes_count -= 1
    else:
        post.likes_count += 1
    
    post.save()
    return redirect(request.META.get('HTTP_REFERER', 'forum-main'))

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        
        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                text=content
            )

    return redirect(request.META.get('HTTP_REFERER', 'forum-main'))

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category', 'image', 'pdf', 'video_file']
    template_name = 'post/update_post.html' 
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('post-detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post/delete_post.html' 
    
    def get_success_url(self):
        return reverse('forum-main')
    
class PostDetailView(DetailView):
    model = Post
    template_name = 'post/detail_post.html' 
    context_object_name = 'post' 