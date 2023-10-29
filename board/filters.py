from django_filters import FilterSet
from .models import *


# class PostFilter(FilterSet):
#     class Meta:
#         model = Post
#         fields = {'user': ['icontains'], 'date': ['lt', 'gt'], 'type': ['exact'], 'title': ['icontains'], 'text': ['icontains']}
#
#
# class CommentFilter(FilterSet):
#     class Meta:
#         model = Post
#         fields = {'user': ['icontains'], 'date': ['lt', 'gt'], 'status': ['exact'], 'text': ['icontains']}