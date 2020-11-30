# import unicodedata

from __future__ import absolute_import

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

# class UsernameField(forms.CharField):
#     def to_python(self, value):
#         return unicodedata.normalize('NFKC', super().to_python(value))
#
#     def widget_attrs(self, widget):
#         return {
#             **super().widget_attrs(widget),
#             'autocapitalize': 'none',
#             'autocomplete': 'username',
#         }
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
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Confirm password"}
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
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
