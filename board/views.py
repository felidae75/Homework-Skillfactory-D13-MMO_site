from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, TemplateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin  # Для ограничения доступа
from django.core.paginator import Paginator  # Для добавления страниц
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy, resolve
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

from .filters import *
from .forms import *
from .models import *

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'post_list'
    ordering = ['-dateCreation']
    paginate_by = 10


class PostsSort(View):
    # Сортировка и вывод страниц
    def get(self, request):
        posts = Post.objects.order_by('-dateCreation')
        p_paginator = Paginator(posts, 1)
        posts = p_paginator.get_page(request.GET.get('page', 1))

        data = {
            'posts': posts,
        }

        return render(request, 'post_list.html', data)


class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'add_post.html'
    form_class = CreatePostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'../{post.id}')


