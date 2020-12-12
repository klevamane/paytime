# import unicodedata

from __future__ import absolute_import

from allauth.account.forms import LoginForm as AllAuthLoginForm
from allauth.account.forms import SignupForm as AllAuthSignupForm
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField
from django.forms import CheckboxInput, TextInput
from django.utils.translation import gettext_lazy as _

from authentication.utils import clean_attr
from user.models import User


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

    class Meta:
        model = User
        # layout where you want the fields to be
        # add enail field here so that it will show up
        # and also the order you want it to showup
        # fields = ["first_name", "last_name", "email"]
        field_classes = {"email": UsernameField}

    def custom_signup(self, request, user):
        """
        Since we are making use of a custom signup form
        we need to account for the newly added fields

        Args:
            request: The request
            user: The user about to be saved
        """
        first_name = clean_attr(self.cleaned_data["first_name"])
        last_name = clean_attr(self.cleaned_data["last_name"])
        user.firstname = first_name
        user.lastname = last_name
        user.save()
