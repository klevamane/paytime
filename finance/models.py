from __future__ import absolute_import

from dirtyfields import DirtyFieldsMixin
from django.db import models

# Create your models here.
from dashboard.models import TimeStampMixin
from finance.validators import validate_account_number
from user.models import User


class BankDetails(DirtyFieldsMixin, TimeStampMixin):
    bank = models.CharField(max_length=30)
    account_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_account_number],
        help_text="Enter your 10 digit account number",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
