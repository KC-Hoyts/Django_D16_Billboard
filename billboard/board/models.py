from ckeditor.fields import RichTextField

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    CATEGORY_LIST = [
        ("tank", "Танки"),
        ('heal', "Хилы"),
        ("dd", "ДД"),
        ("buyers", "Торговцы"),
        ("gildemaster", "Гилдмастеры"),
        ("quest", "Квестгиверы"),
        ("smith", "Кузнецы"),
        ("tanner", "Кожевники"),
        ("potion", "Зельевары"),
        ("spellmaster", "Мастера заклинаний"),

    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    body = RichTextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_LIST)

    def __str__(self):
        return (f'{self.title}')

    def get_absolute_url(self):
        return reverse('post_view', args=[str(self.id)])

class Replies(models.Model):
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)


class RandomNumber(models.Model): # модель для сохранения сгенерированного случайного числа при регистрации
    number = models.IntegerField()
    related_user = models.ForeignKey(User, on_delete=models.CASCADE)
