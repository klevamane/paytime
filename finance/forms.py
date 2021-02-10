from __future__ import absolute_import

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from finance.models import Bank, Banks, Package
from paytime.utils import FAILURE_MESSAGES


class BankForm(forms.ModelForm):
    bank = forms.ModelChoiceField(queryset=Banks.objects.all())

    class Meta:
        model = Bank
        fields = ["bank", "bank_detail", "account_number", "user", "can_update"]
        widgets = {
            "bank": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "user": forms.widgets.HiddenInput(),
        }

    def save(self, commit=False):
        # set the bank details before saving
        instance = super(BankForm, self).save(commit=commit)
        bank_name = instance.bank
        instance.bank_detail = Banks.objects.get(name=bank_name)
        instance.save()


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
            "active",
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

    def save(self):
        super(PackageForm, self).save(commit=False)
        # if create
        if not self.instance.pk:
            self.instance.active = True
        self.instance.save()

    def clean_maximum_amount(self):

        if self.cleaned_data["maximum_amount"] <= self.cleaned_data["minimum_amount"]:
            raise forms.ValidationError(FAILURE_MESSAGES["min_gt_max"])
        return self.cleaned_data["maximum_amount"]
