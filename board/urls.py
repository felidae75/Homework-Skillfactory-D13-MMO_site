from django.views.decorators.cache import cache_page
from django.urls import path
from .views import *

app_name = 'board'
urlpatterns = [
    path('', cache_page(5)(PostListView.as_view()), name='posts_view'),
    path('', PostsSort.as_view()),
    path('<int:pk>/', cache_page(1)(PostDetailView.as_view()), name='post'),
    path('add/', PostCreateView.as_view(), name='create_post'),
    path('<int:pk>/edit', PostUpdate.as_view(), name='update_post'),
    path('<int:pk>/del', PostDelete.as_view(), name='del_post'),
    path('comments', CommentsView.as_view(), name='comments'),
    path('<int:pk>/comment/', Comment.as_view(), name='comment'),
    path('comments/accept/<int:pk>', comment_accept),
    path('comments/delete/<int:pk>', comment_delete),
    path('user/', UpdateProfile.as_view(), name='profile_edit'),
    path('verify/', VerifyCodeView.as_view(), name='verify_page'),
    path('verify/', take_code, name='take_code'),
]