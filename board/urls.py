from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.urls import path
from .views import *

app_name = 'board'
urlpatterns = [
    path('', cache_page(5)(PostListView.as_view()), name='posts_view'),
    path('', PostsSort.as_view()),
    path('<int:pk>/', cache_page(1)(PostDetailView.as_view()), name='post'),
    path('add/', PostCreateView.as_view(), name='create_post'),
]