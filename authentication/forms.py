# import unicodedata

from __future__ import absolute_import

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from authentication.models import User


class SignupForm(UserCreationForm):
    email = (forms.EmailField(),)
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Password"}
        ),
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Confirm password"}
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        required=True,
    )

    class Meta:
        model = User
        # layout where you want the fields to be
        # add enail field here so that it will show up
        # and also the order you want it to showup
        fields = ["firstname", "lastname", "email"]
        field_classes = {"email": UsernameField}
        widgets = {
            "firstname": forms.TextInput(attrs={"placeholder": "Firstname"}),
            "lastname": forms.TextInput(attrs={"placeholder": "Lastname"}),
            "email": forms.TextInput(attrs={"placeholder": "Email"}),
        }

    def clean_first_name(self):
        return strip_tags(self.cleaned_data["firstname"].strip())

    def clean_last_name(self):
        return strip_tags(self.cleaned_data["lastname"].strip())

    def save(self):
        instance = super(SignupForm, self).save(commit=False)
        instance.firstname = self.clean_first_name()
        instance.lastname = self.clean_last_name()
        instance.save()
        return instance
