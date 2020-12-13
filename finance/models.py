from __future__ import absolute_import

from dirtyfields import DirtyFieldsMixin
from django.db import models

# Create your models here.
from dashboard.models import TimeStampMixin
from finance.validators import validate_account_number
from user.models import User


class BankDetails(DirtyFieldsMixin, TimeStampMixin):
    # When a user adds a bank account
    # automatically create a wallet for the user
    bank = models.CharField(max_length=30)
    account_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_account_number],
        help_text="Enter your 10 digit account number",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Bank: {}, #: {}".format(self.bank, self.account_number)


TRANSACTION_TYPE = ["Deposit", "Withrawal"]


class Transactions(DirtyFieldsMixin, TimeStampMixin):
    transaction_type = models.CharField(choices=TRANSACTION_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        choices=["pending", "expired", "done", "closed"], default="pending"
    )
    amount = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return "{} by {}".format(self.transaction_type, self.user.get_full_name())


class Wallet(DirtyFieldsMixin, TimeStampMixin):
    # The balance will be updated upon
    # deposit and withrawal
    # The balance will first be checked before each of these actions
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Balance {}".format(self.balance)

    def do_depost(self):
        # whatever transaction done here should be updated to the transactions Table
        # send the user to paystack AP
        # payment complete?
        # the user is returned and wallet balance is updated
        pass

    def do_withdrawal(self):
        # whatever transaction done here should be updated to the transactions Table
        # the user will request for withrawal
        # we add that to the transactions table as pending
        pass
