from __future__ import absolute_import
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


def index(request):
    return render(request, "partials/base-dashboard.html")


def signup(request):
    form = UserCreationForm()
    context = {"form": form}
    return render(request, "authentication/signup.html", context)


def login(request):
    return render(request, "authentication/login.html")


def forgot_password(request):
    return render(request, "authentication/forgot-pwd.html")


def not_found(request):
    return render(request, "404.html")
