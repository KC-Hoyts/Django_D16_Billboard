import django_filters
from django_filters import FilterSet, CharFilter, ChoiceFilter

from .models import *


class PostsFilter(FilterSet):
   title = django_filters.CharFilter(field_name='title', max_length=100, lookup_expr='icontains')
   body = CharFilter(field_name='body', max_length=100, lookup_expr='icontains')
   category = ChoiceFilter(field_name="category", choices=Post.CATEGORY_LIST)

   class Meta:
       model = Post
       fields = ['category']



