from __future__ import absolute_import

from django.core.exceptions import ValidationError

from paytime.utils import FAILURE_MESSAGES


def validate_account_number(number):
    try:
        int(number)
    except ValueError:
        raise ValidationError(
            FAILURE_MESSAGES["enter_valid_number"].format("account number")
        )
    if len(number) != 10:
        raise ValidationError(FAILURE_MESSAGES["specify_account_digits"].format(10))
