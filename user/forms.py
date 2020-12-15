from __future__ import absolute_import

from django import forms

from user.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "firstname",
            "lastname",
            "address1",
            "area",
            "city",
            "state",
            "email",
            "mobile",
            "date_of_birth",
        ]
