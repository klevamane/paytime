from __future__ import absolute_import
from django.urls import path
from authentication import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("forgot-password", views.forgot_password, name="forgotpwd"),
]
