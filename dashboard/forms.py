from __future__ import absolute_import

from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from finance.models import Package, Payment


class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(decimal_places=2, max_digits=9, required=True)
    # set to_field_name="codename" to use the select option value as "codename"
    # https://docs.djangoproject.com/en/1.10/ref/forms/fields/#django.forms.ModelChoiceField.to_field_name
    package = forms.ModelChoiceField(
        queryset=Package.objects.all(), required=False, to_field_name="codename"
    )
    terms_condition = forms.BooleanField(required=True)

    class Meta:
        model = Payment
        fields = ["amount", "package", "terms_condition"]
        widgets = {
            "package": forms.widgets.Select(attrs={"cursor": "pointer"}),
            "user": forms.widgets.HiddenInput(),
        }
