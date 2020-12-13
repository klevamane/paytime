from __future__ import absolute_import

from dirtyfields import DirtyFieldsMixin
from django.db import models

# Create your models here.
from dashboard.models import TimeStampMixin
from finance.validators import validate_account_number
from user.models import User

Banks = [
    ("access_bank", "Access Bank"),
    ("citibank", "Citibank"),
    ("dynamic_standard_bank", "Dynamic Standard Bank"),
    ("ecobank_ngr", "Ecobank Nigeria"),
    ("fidelity_bank_ngr", "Fidelity Bank Nigeria"),
    ("fbn", "First Bank of Nigeria"),
    ("fcmb", "First City Monument Bank"),
    ("gtb", "Guaranty Trust Bank"),
    ("hb", "Heritage Bank"),
    ("jz", "Jaiz Bank"),
    ("keystone", "Keystone Bank"),
    ("providus", "Providus Bank"),
    ("polaris", "Polaris Bank"),
    ("stanbic", "Stanbic IBTC Bank Nigeria"),
    ("standard_chartered", "Standard Chartered Bank"),
    ("sterling", "Sterling Bank"),
    ("suntrust", "Suntrust Bank Nigeria"),
    ("union_bank", "Union Bank of Nigeria"),
    ("uba", "United Bank for Africa"),
    ("unity_bank", "Unity Bank"),
    ("wema_bank", "Wema Bank"),
    ("zenith_bank", "Zenith Bank"),
]


class Bank(DirtyFieldsMixin, models.Model, TimeStampMixin):
    # When a user adds a bank account
    # automatically create a wallet for the user
    bank = models.CharField(max_length=30, choices=Banks)
    account_number = models.CharField(
        max_length=10,
        validators=[validate_account_number],
        help_text="Enter your 10 digit account number",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bank_details"
    )

    def __str__(self):
        return "Bank: {}, #: {}".format(self.bank, self.account_number)


TRANSACTION_TYPE = [("deposit", "Deposit"), ("withdrawal", "Withdrawal")]
TRANSACTION_STATUS = [
    ("pending", "Pending"),
    ("expired", "Expired"),
    ("done", "Done"),
    ("closed", "Closed"),
    ("none", "None"),
]


class Transactions(DirtyFieldsMixin, models.Model, TimeStampMixin):
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=20)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    status = models.CharField(choices=TRANSACTION_STATUS, default="none", max_length=20)
    amount = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return "{} by {}".format(self.transaction_type, self.user.get_full_name())


class Wallet(DirtyFieldsMixin, models.Model, TimeStampMixin):
    # The balance will be updated upon
    # deposit and withrawal
    # The balance will first be checked before each of these actions
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    book_balance = models.DecimalField(
        null=True, blank=True, decimal_places=2, max_digits=12
    )
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
