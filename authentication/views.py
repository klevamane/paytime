from __future__ import absolute_import

import json

from django.contrib.auth.forms import UserCreationForm
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


def validate_user_email_view(request):
    data = json.loads(request.body)
    email = data["email"]
    if User.objects.filter(email=email).exists():
        return JsonResponse({"email_exists": "Email already exists"}, status=409)
    return JsonResponse({"email_exists": True})


# if read_only:
#            return JsonResponse(
#                {
#                    "result": "failure",
#                    "reason": "You don't have permission to edit this building",  # noqa
#                },
#                status=403,
#            )


def login(request):
    return render(request, "authentication/login.html")


def forgot_password(request):
    return render(request, "authentication/forgot-pwd.html")


def not_found(request):
    return render(request, "404.html")
