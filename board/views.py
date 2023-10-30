from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView, FormView
from django.views import View
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin  # Для ограничения доступа
from django.core.paginator import Paginator  # Для добавления страниц
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import random

from .tasks import *
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if CommentPost.objects.filter(user=self.request.user).filter(post_id=self.kwargs.get('pk')):
            context['is_comment'] = "y"
        elif self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).user:
            context['is_comment'] = "My"
        return context


class PostCreateView(RichTextField, CreateView):
    template_name = 'add_post.html'
    form_class = CreatePostForm
    permission_required = 'board.create_post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = User.objects.get(id=self.request.user.id)
        post.save()
        return redirect(f'../{post.id}')


class PostUpdate(RichTextField, UpdateView):
    template_name = 'add_post.html'
    form_class = CreatePostForm
    permission_required = 'board.change_post'

    def get_object(self, **kwargs):
        id_post = self.kwargs.get('pk')
        return Post.objects.get(pk=id_post)

    def form_valid(self, form):
        post = form.save(commit=False)
        if post.user == User.objects.get(id=self.request.user.id):
            post.save()
            return redirect(f'../{post.id}')


class PostDelete(RichTextField, DeleteView):
    template_name = 'del_post.html'
    queryset = Post.objects.all()
    success_url = '/mmo'
    permission_required = 'board.delete_post'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user == Post.objects.get(pk=self.kwargs.get('pk')).user:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("No")


class CommentsView(ListView):
    model = CommentPost
    template_name = 'comments.html'
    context_object_name = 'comments'

    title = str('')  # Переменная-костыль, так как гет контекст не хочет работать с локальной переменной

    def get_context_data(self, **kwargs):
        context = super(CommentsView, self).get_context_data(**kwargs)
        # Фильтр по айди
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            self.title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            print(self.title)
        context['form'] = CommentFilterForm(self.request.user, initial={'title': self.title})
        context['title'] = self.title
        if self.title:
            post = Post.objects.get(title=self.title)
            context['filter_comments'] = CommentPost.objects.filter(post=post).order_by('-dateCreation')
        else:
            context['filter_comments'] = CommentPost.objects.filter(post__user=self.request.user).order_by(
                '-dateCreation')
        context['mycomments'] = CommentPost.objects.filter(user=self.request.user).order_by('-dateCreation')
        return context

    def post(self, request, *args, **kwargs):
        self.title = self.request.POST.get('title')
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/comments')
        return self.get(request, *args, **kwargs)


@login_required
def comment_accept(request, **kwargs):
    if request.user.is_authenticated:
        comment_post = CommentPost.objects.get(id=kwargs.get('pk'))
        comment_post.status = True
        comment_post.save()
        comment_accept_send_email.delay(comment_id=comment_post.id)
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def comment_delete(request, **kwargs):
    if request.user.is_authenticated:
        comment_post = CommentPost.objects.get(id=kwargs.get('pk'))
        comment_post.delete()
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/accounts/login')


class Comment(RichTextField, CreateView):
    model = CommentPost
    template_name = 'comment.html'
    form_class = CommentForm
    permission_required = 'board.create_comment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        comment_post = form.save(commit=False)
        comment_post.user = User.objects.get(id=self.request.user.id)
        comment_post.post = Post.objects.get(id=self.kwargs.get('pk'))
        comment_post.save()
        # print(comment_post)
        comment_send_email.delay(comment_id=comment_post.id)
        # print(1, comment_send_email)
        return redirect(f'/mmo/{self.kwargs.get("pk")}')


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfile
    success_url = 'profile'
    template_name = 'update_profile.html'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.id
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.groups.filter(name='activated').exists():
            context['is_verify'] = False
        else:
            context['is_verify'] = True
        return context


@login_required
def take_code(request):
    # Код временно сохраняется в базу данных
    if not request.user.groups.filter(name='activated').exists():
        code = random.randint(1000, 9999)
        VerifyCode.objects.create(user=request.user, code=code)

        email_subject = f'MMO: verify e-mail',
        user_emails = [request.user.email, ],

        msg = EmailMultiAlternatives(
            subject=email_subject,
            body=f'Greetings, {request.user.username}! Your verify code {code}'
                 f'Confirm your email \nhttp://127.0.0.1:8000/user/verify',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails
        )

        msg.send()
        return redirect(f'/mmo/verify')


class VerifyCodeView(FormView):
    model = VerifyCode
    form_class = AuthCodeForm
    template_name = 'profile_code.html'

    def form_valid(self, form, **kwargs):
        code_user = VerifyCode.objects.get(user=self.request.user)
        if form.cleaned_data['code'] == code_user.code:
            Group.objects.get(name='Activated').user_set.add(self.request.user)
            # И удаляем из базы данных
            VerifyCode.objects.filter(user=self.request.user).delete()
            return redirect(f'/mmo/user')







