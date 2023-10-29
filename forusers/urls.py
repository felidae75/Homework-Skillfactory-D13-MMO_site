from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.urls import path
from .views import *

app_name = 'users'

urlpatterns = [
]