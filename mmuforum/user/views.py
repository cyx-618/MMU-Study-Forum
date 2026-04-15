from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

#view function
def homepage_hello (request):
    return HttpResponse ('Hi, Welcome to our MMU-Forum.')

#def homepage_hello (request):
    #return render(request, 'user/hello.html', {'name': 'Mosh'})
