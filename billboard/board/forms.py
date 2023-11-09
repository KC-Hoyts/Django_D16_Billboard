from allauth.account.forms import LoginForm, SignupForm

from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

from random import randint

from .models import Post, Replies, RandomNumber


class MyCustomSignupForm(SignupForm):
    username = forms.CharField(max_length=20)
    # first_name = forms.CharField(max_length=20)  #возможно добавление имени, если надо
    # last_name = forms.CharField(max_length=20)   #возможно добавление фамилии, если надо

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        common_users = Group.objects.get(name="Authors")
        user.groups.add(common_users)

        # Отправка сообщения новому пользователю
        if user.first_name:
            appeal = user.first_name
        else:
            appeal = user.username
        subject = 'Добро пожаловать на наш интернет-портал!'
        text = f'{appeal}, вы успешно зарегистрировались на сайте!'
        html = (
            f'<b>{appeal}</b>, вы успешно зарегистрировались на нашей'
            f'<a href="http://127.0.0.1:8000/"> Доске объявлений</a>!'
            f'<br><br>'
            f'<img  width="80%" height="90%" style="box-shadow: 0 0 20px 2px #F00B51" src="https://i.pinimg.com/originals/21/e4/ba/21e4ba1233c60ccd3acca1205cdebe49.jpg" class="rounded-4">'
            f'<br>'
            f'<p style="font-size:11px; color: #696969">Это сообщение создано автоматически, т.к. вы зарегистрировались на портале <b><a href="http://127.0.0.1:8000/"> Доска объявлений</a>.</b></p>'
            f'<p style="font-size:12px; color: #696969">Отвечать на него не нужно.</p>'
        )
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=None, to=[user.email]
        )
        msg.attach_alternative(html, "text/html")
        msg.send()

        # -------------формирование уникального кода для верификации Email`а и сохранение в БД---------
        random_comb = randint(0000, 9999)
        RandomNumber.objects.create(number=int(random_comb), related_user=User.objects.get(id=user.id))
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Replies
        fields = [
            'text'
        ]
        labels = {
            'text' : 'Оставить отклик',
        }
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'Напишите Ваш отклик здесь...'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'body',
            'category'
        ]
        labels = {
            'title' : 'Заголовок',
            'body' : 'Содержание',
            'category' : 'Категория'
        }

        widgets = {
            'title' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Напечатайте заголовок, затем содержимое ниже и в конце выберите категорию :)'}),
            'body' : forms.TextInput(attrs={'class':'form-control'}),
            'category' : forms.Select(attrs={'class':'form-select'},  choices=Post.CATEGORY_LIST),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        body = cleaned_data.get('body')

        if title is not None and len(title) > 40:
            raise ValidationError({
                "title": "Слишком длинный заголовок! Краткость - сестра кликбейта :) Уложитесь в 40 символов."
            })

        if title[0].islower():
            raise ValidationError({
                'title': 'Объявление должно начинаться с заглавной буквы'
            })

        if str(title).lower() == strip_tags(body).lower():
            raise ValidationError("Текст объявления не должен равняться его же заголовку! :( Обзовите объявление по другому")

        return cleaned_data