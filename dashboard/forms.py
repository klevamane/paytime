from __future__ import absolute_import

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from dashboard.models import MessageCenter
from finance.models import Package, Payment
from paytime.utils import FAILURE_MESSAGES, SUCCESS_MESSAGES


class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        decimal_places=2,
        max_digits=12,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter the amount",
            }
        ),
    )
    # set to_field_name="codename" to use the select option value as "codename"
    # ie the value for the dropdown <option value=codename}>
    # https://docs.djangoproject.com/en/1.10/ref/forms/fields/#django.forms.ModelChoiceField.to_field_name
    package = forms.ModelChoiceField(
        queryset=Package.objects.all(),
        required=True,
        to_field_name="codename",
        empty_label="Select a package",
    )
    terms_condition = forms.BooleanField(required=True)

    class Meta:
        model = Payment
        fields = ["amount", "package", "terms_condition"]
        widgets = {
            "package": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "user": forms.widgets.HiddenInput(),
        }

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        # the data must always be returned
        # since the package is required, we can get the value here
        package_codename = str(self.data["package"])
        try:
            package = Package.objects.get(codename=package_codename)
        except Package.DoesNotExist:
            raise forms.ValidationError(FAILURE_MESSAGES["select_pkg_for_amt"])

        # check that the amount lies between the package min and max value
        is_valid_amount = package.minimum_amount <= amount <= package.maximum_amount
        if not is_valid_amount:
            raise forms.ValidationError(
                FAILURE_MESSAGES["amount_specific_range"].format(
                    int(package.minimum_amount), int(package.maximum_amount)
                )
            )
        return amount


class MessageForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = MessageCenter
        fields = ["subject", "message"]
