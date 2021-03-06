from __future__ import absolute_import

from django import forms

from paytime.utils import FAILURE_MESSAGES
from user.models import Document, User


class ProfileForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=[("male", "Male"), ("female", "Female")], required=True
    )

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
            "profile_picture",
            "gender",
        ]

    def __init__(self, *args, **kwargs):
        # remove this kwarg because the form
        # doesn't need it

        disable_fields = kwargs.pop("disable_fields", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        if disable_fields:
            for field in self.fields:
                self[field].field.disabled = True

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get("profile_picture")
        if profile_picture and (profile_picture.size / 1024) > 201:
            raise forms.ValidationError(
                FAILURE_MESSAGES["file_size_limit"].format("image", "200KB")
            )

        return profile_picture


DOCUMENT_CHOICES = (
    ("International passport", "International passport"),
    ("Drivers Licence", "Drivers Licence"),
    ("National Identity", "National Identity"),
    ("Other valid Id", "Other valid Id"),
)


class DocumentForm(forms.ModelForm):
    type = forms.ChoiceField(choices=DOCUMENT_CHOICES, required=True)

    class Meta:
        model = Document
        fields = ["type", "file"]
