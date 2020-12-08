# import unicodedata

from __future__ import absolute_import

from allauth.account.forms import SignupForm as AllAuthSignupForm
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UsernameField,
)
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from authentication.models import User
from authentication.utils import clean_attr


class SignupForm(AllAuthSignupForm):

    first_name = forms.CharField(
        max_length=25,
        min_length=1,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Firstname"),
            }
        ),
    )
    last_name = forms.CharField(
        max_length=25,
        min_length=1,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Lastname"),
            }
        ),
    )

    #     max_length=20,
    #     min_length=1,
    # )
    # email = (forms.EmailField(),)
    # password1 = forms.CharField(
    #     label=_("Password"),
    #     strip=False,
    #     widget=forms.PasswordInput(
    #         attrs={"autocomplete": "new-password", "placeholder": "Password"}
    #     ),
    #     help_text=password_validation.password_validators_help_text_html(),
    #     required=True,
    # )
    # password2 = forms.CharField(
    #     label=_("Password confirmation"),
    #     widget=forms.PasswordInput(
    #         attrs={"autocomplete": "new-password", "placeholder": "Confirm password"}
    #     ),
    #     strip=False,
    #     help_text=_("Enter the same password as before, for verification."),
    #     required=True,
    # )

    class Meta:
        model = User
        # layout where you want the fields to be
        # add enail field here so that it will show up
        # and also the order you want it to showup
        # fields = ["first_name", "last_name", "email"]
        field_classes = {"email": UsernameField}

    # def clean_first_name(self):
    #     return strip_tags(self.cleaned_data["firstname"].strip())
    #
    # def clean_last_name(self):
    #     return strip_tags(self.cleaned_data["lastname"].strip())

    def custom_signup(self, request, user):
        first_name = clean_attr(self.cleaned_data["first_name"])
        last_name = clean_attr(self.cleaned_data["last_name"])
        user.firstname = first_name
        user.lastname = last_name
        user.save()
