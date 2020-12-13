from __future__ import absolute_import

from django.core.exceptions import ValidationError


def validate_account_number(number):
    try:
        int(number)
    except ValueError:
        raise ValidationError("Enter a valid account number")
    if len(number) != 10:
        raise ValidationError("10 digit account number is required")
