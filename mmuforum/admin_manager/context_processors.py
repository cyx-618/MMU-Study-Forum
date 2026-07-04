from user.models import Major

def global_context(request):
    return {
        'majors': Major.objects.all()
    }