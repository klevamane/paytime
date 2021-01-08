from __future__ import absolute_import

import datetime

from dirtyfields import DirtyFieldsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum

from dashboard.models import TimeStampMixin
from finance.validators import validate_account_number
from paytime.utils import FAILURE_MESSAGES
from user.models import User

BANKS = [
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


class Bank(DirtyFieldsMixin, TimeStampMixin):
    # When a user adds a bank account
    # automatically create a wallet for the user
    bank = models.CharField(max_length=30, choices=BANKS, default="access_bank")
    account_number = models.CharField(
        max_length=10,
        validators=[validate_account_number],
        help_text="Enter your 10 digit account number",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=True)
    can_update = models.BooleanField(default=False)

    def __str__(self):
        return "Bank: {}, #: {}".format(self.bank, self.account_number)


class InvestmentPackage(DirtyFieldsMixin, TimeStampMixin):
    name = models.CharField(max_length=20)
    roi = models.IntegerField()
    duration = models.PositiveIntegerField(verbose_name="Duration in days")
    working_days_only = models.BooleanField(default=True)
    payment_duration = models.PositiveIntegerField()
    minimum_amount = models.DecimalField(decimal_places=2, max_digits=9)
    maximum_amount = models.DecimalField(decimal_places=2, max_digits=9)


TRANSACTION_TYPE = [("deposit", "Deposit"), ("withdrawal", "Withdrawal")]
TRANSACTION_STATUS = [
    ("pending", "Pending"),
    ("expired", "Expired"),
    ("completed", "completed"),
    ("closed", "Closed"),
    ("none", "None"),
]


class Transactions(DirtyFieldsMixin, TimeStampMixin):
    transaction_type = models.CharField(choices=TRANSACTION_TYPE, max_length=20)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    status = models.CharField(choices=TRANSACTION_STATUS, default="none", max_length=20)
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    for_package = models.BooleanField(default=False)

    def __str__(self):
        return "{} by {}".format(self.transaction_type, self.user.get_full_name())


class Wallet(DirtyFieldsMixin, TimeStampMixin):
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

    def do_depost(self, amount, user, for_package=False, status="completed"):
        self.balance += int(amount)
        self.save()
        self._make_transaction(amount, user, for_package, status)

    def _make_transaction(
        self, amount, user, for_package=False, tnx_type="deposit", status="pending"
    ):
        transaction = Transactions(
            transaction_type=tnx_type,
            user=user,
            amount=int(amount),
            status=status,
            for_package=for_package,
        )
        transaction.save()

    def do_withdrawal(self, amount, user, for_package=False, status="pending"):
        try:
            if int(amount) <= int(self.balance):
                self.balance -= amount
                self._make_transaction(amount, user, for_package, "withdrawal", status)
                return
        except TypeError:
            raise ValidationError(
                message=FAILURE_MESSAGES["enter_valid_amount"], code=400
            )

        raise ValidationError(message=FAILURE_MESSAGES["insufficient_funds"], code=400)

    @property
    def total_withrawals(self):
        return self._get_transaction_total("withdrawal")

    @property
    def total_deposits(self):
        return self._get_transaction_total("deposit")

    def latest_transactions(self):
        # print this with .query to view the sql
        return self.user.transactions.all().order_by("-created_at")[0:5]

    def _get_transaction_total(self, tnx_type):
        return (
            self.user.transactions.filter(transaction_type=tnx_type).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0
        )


PACKGE_CHOICES = [
    ("fresher", "Fresher"),
    ("bronze", "Bronze"),
    ("silver", "Silver"),
    ("gold", "Gold"),
]


class Package(DirtyFieldsMixin, TimeStampMixin):
    name = models.CharField(max_length=30, unique=True)
    minimum_amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    maximum_amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    return_on_investmentent = models.PositiveIntegerField()
    codename = models.CharField(max_length=30, unique=True)
    days = models.IntegerField()
    level = models.CharField(choices=PACKGE_CHOICES, default="silver", max_length=30)

    @property
    def is_new(self):
        return (self.created_at - datetime.datetime.now().date()).days < 60

    def __str__(self):
        return self.name


class Payment(DirtyFieldsMixin, TimeStampMixin):
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING, max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default="open")


INVESTMENT_STATUS = [
    ("active", "Active"),
    ("cancelled", "Cancelled"),
    ("completed", "Completed"),
    ("pending", "Pending"),
    ("processing", "Processing"),
    ("success", "Success"),
    ("transfer", "Transfer"),
]


class Investment(DirtyFieldsMixin, TimeStampMixin):
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING)
    status = models.CharField(
        choices=INVESTMENT_STATUS, max_length=20, default="pending"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)


ROI_ACTIONS = [
    ("transfer", "transfer"),
    ("no_action", "No Action"),
    ("payment_completed", "Payment completed"),
]


class RoiSchedule(DirtyFieldsMixin, TimeStampMixin):
    maturity_date = models.DateField(db_index=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    status = models.CharField(
        choices=INVESTMENT_STATUS, max_length=20, default="pending"
    )
    action = models.CharField(
        choices=INVESTMENT_STATUS, max_length=20, default="pending"
    )
    roi_amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
