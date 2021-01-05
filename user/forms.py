from __future__ import absolute_import

from django import forms

from user.models import Document, User


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


DOCUMENT_CHOICES = (
    ("International passport", "International passport"),
    ("Drivers Licence", "Drivers Licence"),
    ("National Identity", "National Identity"),
    ("Other valid Id", "Other valid Id"),
)


class DocumentForm(forms.ModelForm):
    type = forms.ChoiceField(choices=DOCUMENT_CHOICES)

    class Meta:
        model = Document
        fields = ["type", "file"]
