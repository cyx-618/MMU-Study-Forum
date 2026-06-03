from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from post.models import Post, Comment
from django.http import JsonResponse

# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def admin_main(request):
    posts = Post.objects.all().order_by('-date_posted')

    context = {
        'posts': posts,
    }
    return render(request, 'admin_manager/admin_main.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_post_detail(request, post_id):
    post=get_object_or_404 (Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'admin_manager/admin_post_detail.html', context)

@user_passes_test(lambda u: u.is_superuser)
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.likes_count.filter(id=request.user.id).exists():
        comment.likes_count.remove(request.user)
        liked = False
    else:
        comment.likes_count.add(request.user)
        liked = True

    return JsonResponse({
        'liked': liked, 
        'count': comment.likes_count.count()
    })