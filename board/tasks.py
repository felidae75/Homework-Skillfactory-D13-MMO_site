from celery import shared_task
from django.core.mail.message import EmailMultiAlternatives
from django.core.mail import send_mail
from datetime import timedelta
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import *


DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL



@shared_task
def comment_send_email(comment_id):
    comment_post = CommentPost.objects.get(id=comment_id)

    email_subject = f'MMO: Someone comment you',
    user_emails = [comment_post.post.user.email, ]

    msg = EmailMultiAlternatives(
            subject=email_subject,
            body=f'Greetings, {comment_post.post.user}! New comment in your advert!\n'
                 f'Read here\nhttp://127.0.0.1:8000/comments/{comment_post.post.id}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails,
        )

    msg.send()

@shared_task
def comment_accept_send_email(comment_id):
    comment_post = CommentPost.objects.get(id=comment_id)
    email_subject = f'MMO: Your Comment accepted!'
    user_emails = [comment_post.post.user.email, ]
    msg = EmailMultiAlternatives(
            subject=email_subject,
            body=f'Greetings, <b.{comment_post.user}</p>, in advert {comment_post.post.title} accepted your comment!\n'
                 f'Watch accepted comments:\nhttp://127.0.0.1:8000/comments',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=user_emails
        )
    msg.send()


@shared_task
def send_mail_monday_8am():
    # Создаем список всех объявлений, созданных за последние 7 дней (list_week_posts)
    now = timezone.now()
    list_week_posts = list(Post.objects.filter(dateCreation__gte=now - timedelta(days=7)))
    if list_week_posts:
        for user in User.objects.filter():
            list_posts = ''
            for post in list_week_posts:
                list_posts += f'\n{post.title}\nhttp://127.0.0.1:8000/mmo/{post.id}'
            msg = EmailMultiAlternatives(
                subject=f'MMO. Weekly news',
                body=f'Greetings, {user.username}!\nWeekly news'
                        f'\n{list_posts}',
                from_email=DEFAULT_FROM_EMAIL,
                to=[user.email, ],
            )
            msg.send()
