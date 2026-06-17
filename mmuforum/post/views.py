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
from user.models import Feedback, Notification
from django.urls import reverse
from django.urls import reverse_lazy

from django.contrib import messages
from .models import ReportComment, ReportPost
from .forms import PostReportForm, CommentReportForm
from django.db.models import Q

from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

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
            is_deleted=False
    ).order_by('-date_posted').prefetch_related('comments', 'likes')

        search_query = request.GET.get('q', '').strip()
        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            ).distinct()
    
        context = {
            'posts': posts,
            'major_name': major_name,
            'title': f'{major_name} Forum',
            'search_query': search_query,
        }
        #return render(request, 'post/major_forum.html', {'posts': posts, 'major_name': major_name})
        return render(request, 'post/major_forum.html', context)


@login_required
def like_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'},status=400)

    post= get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked= False

    else:
        liked=True

        if post.author != request.user:
            notification_exists = Notification.objects.filter(
                receiver=post.author,
                sender=request.user,
                notification_type='post_like',
                post=post,
                is_read=False
            ).exists()

            if not notification_exists:
                Notification.objects.create(
                    receiver=post.author,
                    sender=request.user,
                    notification_type='post_like',
                    post=post
                )

            if post.author.email:
                subject = f"Someone liked your post: {post.title} on MMU Forum!"
                current_site = request.build_absolute_uri('/')[:-1]
                #post_url = f"{current_site}/post/{post.id}/"
                email_body = f"""
Hi {post.author.username},

Great news! {request.user.username} just liked your post titled "{post.title}" on MMU Forum.

You can view your post here: 

From MMU Forum Team
"""
                try:
                    send_mail(
                        subject, 
                        email_body, 
                        settings.EMAIL_HOST_USER,
                        [post.author.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

    return JsonResponse({
        'liked': liked,
        'count': post.likes.count()
    })


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

            if parent_object:
                Notification.objects.create(
                    receiver=parent_object.user,
                    sender=request.user,
                    notification_type='comment_reply',
                    post=post
                )

                if parent_object.user.email:
                    subject = f"Someone replied to your comment on MMU Forum!"
                    current_site = request.build_absolute_uri('/')[:-1]
                    #post_url = f"{current_site}/post/{post.id}/"

                    email_body = f"""
Hi {parent_object.user.username},

Great news! {request.user.username} just replied to your comment on the post titled "{post.title}" on MMU Forum.

You can view the post here:

From MMU Forum Team
"""
                try:
                    send_mail(
                        subject, 
                        email_body, 
                        settings.EMAIL_HOST_USER,
                        [parent_object.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

            else:
                if post.author != request.user:
                    Notification.objects.create(
                        receiver=post.author,
                        sender=request.user,
                        notification_type='post_comment',
                        post=post
                    )
                
                if post.author.email:
                    subject = f"New comment on your post: {post.title} on MMU Forum!"
                    current_site = request.build_absolute_uri('/')[:-1]
                    #post_url = f"{current_site}/post/{post.id}/"
                    email_body = f"""
Hi {post.author.username},

Great news! {request.user.username} just commented on your post titled "{post.title}" on MMU Forum.

You can view your post here:

From MMU Forum Team
                    """
                try:
                    send_mail(
                        subject, 
                        email_body, 
                        settings.EMAIL_HOST_USER,
                        [post.author.email],
                        fail_silently=False,
                    )

                except Exception as e:
                    print(f"Error sending email: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'forum-main'))


@login_required
def like_comment(request, comment_id):
    comment=get_object_or_404(Comment, id=comment_id)
    if comment.likes_count.filter(id=request.user.id).exists():
        comment.likes_count.remove(request.user)
    else:
        comment.likes_count.add(request.user)

        if comment.user != request.user:
            notification_exists = Notification.objects.filter(
                receiver=comment.user,
                sender=request.user,
                notification_type='comment_like',
                post=comment.post,
                is_read=False
            ).exists()

            if not notification_exists:
                Notification.objects.create(
                    receiver=comment.user,
                    sender=request.user,
                    notification_type='comment_like',
                    post=comment.post
                )

            if comment.user.email:
                subject = f"Someone liked your comment on MMU Forum!"
                current_site = request.build_absolute_uri('/')[:-1]
                #post_url = f"{current_site}/post/{comment.post.id}/"

                email_body = f"""
Hi {comment.user.username},

Great news! {request.user.username} just liked your comment on the post titled "{comment.post.title}" on MMU Forum.

You can view the post here:

From MMU Forum Team
"""
            try:
                send_mail(
                    subject, 
                    email_body, 
                    settings.EMAIL_HOST_USER,
                    [comment.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {e}")

    return redirect(request.META.get('HTTP_REFERER', 'forum-main'))


@login_required
def report_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    existing_report = ReportPost.objects.filter(post=post, reporter=request.user).first()
    
    if existing_report:
        messages.warning(request, 'You have already reported this post.')
        return redirect('forum-main')
    
    if request.method == 'POST':
        form = PostReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.post = post
            report.reporter = request.user
            report.save()

            post.is_reported = True
            post.save()

            admins = User.objects.filter(is_superuser=True)
            admin_emails = [admin.email for admin in admins if admin.email]

            for admin_user in admins:
                Notification.objects.create(
                    receiver=admin_user,
                    sender=request.user,
                    notification_type='new_report',
                    content_object=report,
                    post=None
                )

            if admin_emails:
                subject = f"Post Reported: {post.title}"
                current_site = request.build_absolute_uri('/')[:-1]
                post_url = f"{current_site}/post/{post.id}/"
                email_body = f"""
Hi Admin,

A post has been reported on MMU Forum.

Details:
Reporter: {request.user.username}
Post Title: {post.title}
Reason: {report.get_reason_display()}

You can review the post here: 

Best regards,
MMU Forum System
"""
                try:
                    send_mail(
                        subject, 
                        email_body, 
                        settings.EMAIL_HOST_USER,
                        admin_emails,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

            messages.success(request, 'Thank you for your report. We will review it shortly.')
            return redirect('forum-main')
    else:
        form = PostReportForm()
    
    context = {
        'form': form,
        'post': post,
        'reported_post': post,
    }
    return render(request, 'post/report_post.html', context)


@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    
    existing_report = ReportComment.objects.filter(comment=comment, reporter=request.user).first()
    
    if existing_report:
        messages.warning(request, 'You have already reported this comment.')
        return redirect('forum-main')
    
    if comment.user == request.user:
        messages.warning(request,'You cannot report your own comment.')
        return redirect('forum-main')
    
    if request.method == 'POST':
        form = CommentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.comment = comment
            report.reporter = request.user
            report.save()

            admins = User.objects.filter(is_superuser=True)
            admin_emails = [admin.email for admin in admins if admin.email]

            for admin_user in admins:
                Notification.objects.create(
                    receiver=admin_user,
                    sender=request.user,
                    notification_type='new_report',
                    content_object=report,
                    post=None
                )

            if admin_emails:
                subject = f"Post Reported: {post.title}"
                current_site = request.build_absolute_uri('/')[:-1]
                post_url = f"{current_site}/post/{post.id}/"
                email_body = f"""
Hi Admin,

A comment has been reported on MMU Forum.

Details:
Reporter: {request.user.username}
Comment Author:{comment.user.username}
Comment Content: {comment.text[:200]}...
Reason: {report.get_reason_display()}

You can review the post here: 

Best regards,
MMU Forum System
"""
                try:
                    send_mail(
                        subject, 
                        email_body, 
                        settings.EMAIL_HOST_USER,
                        admin_emails,
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email: {e}")

            messages.success(request, 'Thank you for your report. We will review it shortly.')
            return redirect('forum-main')
    else:
        form = CommentReportForm()
    
    context = {
        'form': form,
        'comment': comment,
        'reported_post': post,
        'post':post,
    }
    return render(request, 'post/report_comment.html', context)


class  PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'post/main.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_queryset(self):
        search_type = self.request.GET.get('search_type', 'posts')
        search_query = self.request.GET.get('q','').strip()

        queryset = Post.objects.filter(is_deleted=False)
        reported_ids = ReportPost.objects.filter(reporter=self.request.user).values_list('post_id', flat=True)
        queryset = queryset.exclude(id__in=reported_ids).order_by('-date_posted')

        search_query = self.request.GET.get('q', '').strip()
        
        if search_query:
            if search_type == 'posts':
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(content__icontains=search_query) 
            ).distinct()
            elif search_type == 'users':
                queryset = Post.objects.none()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query= self.request.GET.get('q', '').strip()
        search_type = self.request.GET.get('search_type','posts')

        context['search_type'] = search_type
        context['search_query'] = search_query
        context['search_type_display'] = 'Post' if search_type == 'posts' else 'User'
        
        users = []
        if search_query and search_type == 'users':
            from django.contrib.auth.models import User
            users = User.objects.filter(username__icontains=search_query)
            context['users'] = users

        if search_query and search_type == 'posts':
            reported_ids = ReportPost.objects.filter(reporter=self.request.user).values_list('post_id', flat=True)
            total_queryset = Post.objects.filter(is_deleted=False).exclude(id__in=reported_ids).filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
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


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post/detail_post.html' 
    context_object_name = 'post' 