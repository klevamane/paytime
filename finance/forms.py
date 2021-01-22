from __future__ import absolute_import

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from finance.models import Bank, Package
from paytime.utils import FAILURE_MESSAGES


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

        widgets = {
            "level": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "name": forms.TextInput(attrs={"placeholder": "Enter the package name"}),
            "minimum_amount": forms.TextInput(
                attrs={"placeholder": "Enter the minimum amount"}
            ),
            "maximum_amount": forms.TextInput(
                attrs={"placeholder": "Enter the maximum amount"}
            ),
            "return_on_investmentent": forms.TextInput(
                attrs={"placeholder": "Enter the roi (number)"}
            ),
            "days": forms.TextInput(attrs={"placeholder": "Enter the number of days"}),
        }

    def clean_maximum_amount(self):

        if self.cleaned_data["maximum_amount"] <= self.cleaned_data["minimum_amount"]:
            raise forms.ValidationError(FAILURE_MESSAGES["min_gt_max"])
        return self.cleaned_data["maximum_amount"]
