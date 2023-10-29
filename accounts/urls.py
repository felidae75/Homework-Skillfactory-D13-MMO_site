from django.urls import path, include
from .views import *


urlpatterns = [
  path('', include('allauth.urls')),
]