# import unicodedata

from __future__ import absolute_import

from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField

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
    email = forms.EmailField()

    class Meta:
        model = User
        # layout where you want the fields to be
        # add enail field here so that it will show up
        # and also the order you want it to showup
        fields = ["firstname", "lastname", "email"]
        field_classes = {"email": UsernameField}
