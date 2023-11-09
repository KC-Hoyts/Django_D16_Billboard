from django import template

from board.models import Post, Replies

register = template.Library()


@register.filter(takes_context=True)
def readable_category(category, **kwargs):
    for model_category in Post.CATEGORY_LIST:
        if category == model_category[0]:
            return model_category[1]


@register.filter(takes_context=True)
def month_translation(date, **kwargs):
    month_names = [
        'Января',
        'Февраля',
        'Марта',
        'Апреля',
        'Мая',
        'Июня',
        'Июля',
        'Августа',
        'Сентября',
        'Октября',
        'Ноября',
        'Декабря',
    ]
    for ind, month in enumerate(month_names):
        if ind == date.month-1:
            return f'{date.day} {month} {date.year} в'


@register.filter(takes_context=True)
def replies_amount(context, **kwargs):
    amount = len(Replies.objects.filter(comment_post=Post.objects.get(pk=context.id)))
    return amount