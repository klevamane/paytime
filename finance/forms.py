from __future__ import absolute_import

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from finance.models import Bank, Package


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ["bank", "account_number", "user", "can_update"]
        widgets = {
            "bank": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "user": forms.widgets.HiddenInput(),
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = [
            "name",
            "minimum_amount",
            "maximum_amount",
            "return_on_investmentent",
            "days",
            "level",
        ]

    def clean_maximum_amount(self):
        import pdb

        pdb.set_trace()

        if self.cleaned_data["maximum_amount"] < self.cleaned_data["minimum_amount"]:
            raise ValidationError("Maximum amount must be greater than minimum amount")
        return self.cleaned_data["maximum_amount"]
