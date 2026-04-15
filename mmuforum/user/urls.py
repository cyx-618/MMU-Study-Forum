from django.urls import path
from . import views

#URLconf

#urlpatterns = [
#path('_urlname_',views._functionname_)
#]
#写完之后去urls.py(main)

urlpatterns = [
path('homepage/',views.homepage_hello)
]