from __future__ import absolute_import

from django import forms
from django.utils.translation import gettext_lazy as _

from finance.models import Bank


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ["bank", "account_number", "user", "can_update"]
        widgets = {
            "bank": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "user": forms.widgets.HiddenInput(),
        }
