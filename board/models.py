from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.db.models import OneToOneField


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128, verbose_name='Title')
    text = RichTextField()
    CATEGORY = (('tanks', 'Танки'),  # Категории, которые надо указать при публикации
                ('healers', 'Хилы'),
                ('damage_dealers', 'ДД'),
                ('dealers', 'Торговцы'),
                ('gild_masters', 'Гилдмастеры'),
                ('quest_givers', 'Квестгиверы'),
                ('blacksmiths', 'Кузнецы'),
                ('tanners', 'Кожевники'),
                ('potion_makers', 'Зельевары'),
                ('spell_masters', 'Мастера заклинаний'))
    category = models.CharField(max_length=24, choices=CATEGORY, verbose_name='Category')

    def __str__(self):
        return f'{self.user}, {self.title}, {self.category}, {self.dateCreation}'


class CommentPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dateCreation = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField(verbose_name="Message")
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}, {self.text}, {self.dateCreation}, {self.status}'


# Костыль, чтобы сохранить код
class VerifyCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.IntegerField(default=0)

