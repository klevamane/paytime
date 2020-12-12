from __future__ import absolute_import

from django.core.exceptions import ValidationError


def validate_account_number(number):
    if number and not (number.is_numeric and len(number) == 10):
        raise ValidationError("Enter a valid account number")
