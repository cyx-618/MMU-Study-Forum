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

from django.contrib import messages
from .models import Post, Report
from .forms import ReportForm
from django.db.models import Q

# Create your views here.
def main(request):
    context = {
        #'posts': Post.objects.all().prefetch_related('comments','likes'),
        'posts': Post.objects.filter(is_deleted=False).prefetch_related('comments','likes'),
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
        posts = Post.objects.filter(
            author__user_profile__major__major_name=major_name,
        is_hidden=False
    ).order_by('-date_posted').prefetch_related('comments', 'likes')

        context = {
            'posts': posts,
            'major_name': major_name,
            'title': f'{major_name} Forum'
        }
        #return render(request, 'post/major_forum.html', {'posts': posts, 'major_name': major_name})
        return render(request, 'post/major_forum.html', context)

#yj
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
        parent_id = request.POST.get('parent_id')
        parent_object = None

        if content:
            if parent_id and parent_id.strip():
                target_comment = Comment.objects.filter(id=parent_id).first()
                if target_comment.parent_comment:
                    parent_object = target_comment.parent_comment
                else:
                    parent_object = target_comment

            Comment.objects.create(
                post=post,
                user=request.user,
                text=content,
                parent_comment=parent_object
            )

    return redirect(request.META.get('HTTP_REFERER', 'forum-main'))

@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    existing_report = Report.objects.filter(post=post, reporter=request.user).first()
    
    if existing_report:
        messages.warning(request, 'You have already reported this post.')
        return redirect('forum-main')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()

            report_count = Report.objects.filter(post=post).count()
            if report_count >= 1: 
                post.is_reported = True
                post.is_deleted = True
                post.save()
            messages.success(request, 'Thank you for your report. We will review it shortly.')
            return redirect('forum-main')
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'post': post,
        'reported_post': post,
    }
    return render(request, 'post/report_post.html', context)

def search_posts(request):
    search_query = request.GET.get('q', '').strip()
    posts = Post.objects.filter(is_deleted=False).order_by('-date_posted')
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        ).distinct()
    
    major_name = request.GET.get('major', '')
    if major_name:
        posts = posts.filter(author__user_profile__major__major_name=major_name)
    
    context = {
        'posts': posts,
        'search_query': search_query,
        'total_results': posts.count(),
        'majors': ['FCI', 'FCM', 'FOM', 'FCA', 'FAC', 'FAIE', 'FOL', 'FOB'],  # 专业列表
        'selected_major': major_name,
    }
    return render(request, 'post/search_results.html', context)

class  PostListView(ListView):
    model = Post
    template_name = 'post/main.html' #<app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_queryset(self):
        queryset = Post.objects.filter(is_deleted=False).order_by('-date_posted')

        search_query = self.request.GET.get('q', '').strip()
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query= self.request.GET.get('q', '')
        context['search_query'] = search_query
        
        if search_query:
            total_queryset = Post.objects.filter(is_deleted=False).filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            ).distinct()
            context['total_results'] = total_queryset.count()
        else:
            context['total_results'] = None
            
        return context


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