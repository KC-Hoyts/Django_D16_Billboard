from django.urls import path, re_path
from .views import SignUp, confirm_email

urlpatterns = [
    path('signup', SignUp.as_view(), name='signup'),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        confirm_email.as_view),

]
