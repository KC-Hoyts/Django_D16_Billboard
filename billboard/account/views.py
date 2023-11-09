from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, View
from .forms import SignUpForm
from django.http import HttpResponse
from django.shortcuts import render
from allauth.account.models import EmailAddress



class SignUp(CreateView):
    model = User
    form_class = SignUpForm
    success_url = '/accounts/login'

    template_name = 'registration/signup.html'
