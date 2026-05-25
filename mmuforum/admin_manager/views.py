from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from post.models import Post

# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def admin_main(request):
    posts = Post.objects.all().order_by('-date_posted')

    context = {
        'posts': posts,
    }
    return render(request, 'admin_manager/admin_main.html', context)