from __future__ import absolute_import

import json

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render

from authentication.forms import SignupForm
from authentication.models import User


def index(request):
    return render(request, "partials/base-dashboard.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
        return render(request, "authentication/signup.html", {"form": form})
    form = SignupForm()
    context = {"form": form}
    return render(request, "authentication/signup.html", context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if not user:
                return redirect("login")
            django_login(request, user)
            return redirect("index")
    context = {"form": AuthenticationForm()}
    return render(request, "authentication/login.html", context)


def validate_user_email_view(request):
    data = json.loads(request.body)
    msg = JsonResponse({"valid_email": True}, status=200)
    email = data["email"]
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"email_error": "Enter a valid email"}, status=400)

    if User.objects.filter(email=email).exists():
        msg = JsonResponse({"email_error": "Email already exists"}, status=409)
    return msg


def forgot_password(request):
    return render(request, "authentication/forgot-pwd.html")


def not_found(request):
    return render(request, "404.html")


# if read_only:
#            return JsonResponse(
#                {
#                    "result": "failure",
#                    "reason": "You don't have permission to edit this building",  # noqa
#                },
#                status=403,
#            )
