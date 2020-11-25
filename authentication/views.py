from __future__ import absolute_import
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "partials/base-dashboard.html")


def signup(request):
    return render(request, "authentication/signup.html")


def login(request):
    return render(request, "authentication/login.html")


def forgot_password(request):
    return render(request, "authentication/forgot-pwd.html")