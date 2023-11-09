from django import template
from django.contrib.auth.models import User
from django.shortcuts import redirect

from board.models import *


register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
   d = context['request'].GET.copy()
   for k, v in kwargs.items():
       d[k] = v
   return d.urlencode()


@register.simple_tag(takes_context=True)
def number_generation(context, **kwargs):
    return RandomNumber.objects.get(related_user=User.objects.get(username=context["user_display"])).number


@register.simple_tag(takes_context=True)
def url_address(context, **kwargs):
    return redirect('my_account_confirm_email', pk=User.objects.get(username=context["user"]).id)



