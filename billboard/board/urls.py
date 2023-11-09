from django.urls import path, re_path
from .views import *


urlpatterns = [
    path('', PostsList.as_view(), name='post_list'),
    path('<int:pk>', PostView.as_view(), name='post_view'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('search/<int:pk>', PostView.as_view(), name='post_view_from_search_page'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('my_posts/', PersonalPostsList.as_view(), name='my_posts_list'),
    path('my_posts/<int:pk>', PostView.as_view(), name='post_view_from_my_posts'),
    path('repy_on_comment/<int:pk>', CommentReply.as_view(), name='reply_comment'),
    path("email-confirmation/<int:pk>", MyEmailAddressConfirmation.as_view(), name="my_account_confirm_email"),


]