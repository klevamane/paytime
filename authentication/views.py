from __future__ import absolute_import

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from authentication.forms import SignupForm


def index(request):
    return render(request, "partials/base-dashboard.html")


def signup(request):
    form = SignupForm(request.POST)
    context = {"form": form}
    if request.method == "POST":
        import pdb

        pdb.set_trace()
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            return render(request, "authentication/signup.html", context)
    form = SignupForm()
    context = {"form": form}
    return render(request, "authentication/signup.html", context)


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
