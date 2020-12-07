from __future__ import absolute_import

import json
import logging

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View

from authentication.forms import SignupForm
from authentication.models import User
from authentication.utils import clean_attr
from paytime.utils import SUCCESS_MESSAGES, send_email, token_generator

log = logging.getLogger("api")


def index(request):
    return render(request, "partials/base-dashboard.html")


class SignUp(View):
    def get(self, request):
        context = {"form": SignupForm()}
        return render(request, "authentication/signup.html", context)

    @transaction.atomic()
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.instance
            activate_url = self._get_activation_url(request, user)
            messages.success(request, SUCCESS_MESSAGES["account_created"])
            send_email(
                "Activate your account on Paytime",
                SUCCESS_MESSAGES["kindly_verify"].format(
                    user.get_full_name(), activate_url
                ),
                "noteply@paytime.come",
                "onengiye.richard@gmail.com",
            )
            return redirect("signup")
        return render(request, "authentication/signup.html", {"form": form})

    def _get_activation_url(self, request, user):
        domain = get_current_site(request).domain
        # TODO we can add token_generated_at to the user model
        # so that in the validation we can determin the expiry of the token
        # or perhaps we can attach an encode timestamo with an attached secret
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token_generator.make_token(user)},
        )
        return "http://" + domain + url


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        if request.user.is_authenticated:
            pass
            # todo return to dashboard
        if form.is_valid():
            email = clean_attr(form.cleaned_data.get("username"))
            password = clean_attr(form.cleaned_data.get("password"))
            user = authenticate(username=email, password=password)
            if not user:
                return render(request, "authentication/login.html", {"form": form})
            if not user.email_verified:
                # Todo
                pass
            if not user.is_active:
                # Todo
                pass

            # TODO if user is an admin, we can redirect
            # the user to another url
            django_login(request, user)
            return redirect("index")
        return render(request, "authentication/login.html", {"form": form})
    # chec if a message was passed to the view
    message = request.GET.get("message")
    if message:
        messages.info(request, message)
    context = {"form": AuthenticationForm()}
    return render(request, "authentication/login.html", context)


def validate_user_email_view(request):
    """AJAX call"""
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


def signout(request):
    logout(request)
    return redirect("/")


# classed based view
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            # if it's false it means the user has already
            # made use of this token, it checks if any part of the user
            # was changed
            # TODO: we can also add a timestampt to the
            if not token_generator.check_token(user, token):
                # TODO we should also check if the token is expired, can we check for that?
                messages.info(request, "Your email is already verified and activated")
                return redirect("login")

            if user.is_active:
                url = reverse("login")
                return redirect(url + "?message=already activated")
            user.is_active = True
            user.save()
            messages.success(request, SUCCESS_MESSAGES["verified"])
            return redirect("login")
        except Exception as e:
            log.error("This error occured - {}".format(e))

        messages.success(request, SUCCESS_MESSAGES["verified"])
        return render(request, "authentication/login.html")


# if read_only:
#            return JsonResponse(
#                {
#                    "result": "failure",
#                    "reason": "You don't have permission to edit this building",  # noqa
#                },
#                status=403,
#            )
