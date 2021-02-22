from __future__ import absolute_import

import datetime
import re

from dirtyfields import DirtyFieldsMixin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q, Sum
from django.template.defaultfilters import floatformat

from dashboard.models import TimeStampMixin
from finance.validators import validate_account_number, validate_number
from paytime.utils import FAILURE_MESSAGES
from user.models import User

pattern = re.compile(" ")

BANKS = [
    ("access-bank", "Access Bank"),
    ("access-bank-diamond", "Access Bank (Diamond)"),
    ("alat-by-wema", "ALAT by WEMA"),
    ("asosavings", "ASO Savings and Loans"),
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


class Banks(DirtyFieldsMixin, TimeStampMixin):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    code = models.CharField(max_length=50, unique=True)
    country = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)


class Bank(DirtyFieldsMixin, TimeStampMixin):
    # When a user adds a bank account
    # automatically create a wallet for the user
    # bank = models.CharField(max_length=30, default="access-bank")

    account_number = models.CharField(
        max_length=10,
        validators=[validate_account_number],
        help_text="Enter your 10 digit account number",
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_update = models.BooleanField(default=False)
    bank_detail = models.ForeignKey(
        Banks, on_delete=models.CASCADE, null=True, blank=True
    )
    # this code is used in initiating transfer by paystack
    # https://paystack.com/docs/transfers/single-transfers
    recipient_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "Bank: {}, #: {}".format(self.bank_detail.name, self.account_number)


class InvestmentPackage(DirtyFieldsMixin, TimeStampMixin):
    name = models.CharField(max_length=20)
    roi = models.IntegerField()
    duration = models.PositiveIntegerField(verbose_name="Duration in days")
    working_days_only = models.BooleanField(default=True)
    payment_duration = models.PositiveIntegerField()
    minimum_amount = models.DecimalField(decimal_places=2, max_digits=9)
    maximum_amount = models.DecimalField(decimal_places=2, max_digits=9)

    def __str__(self):
        return "{}".format(self.name)


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
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return "Balance {}".format(self.balance)

    def do_depost(self, amount, user, for_package=False, status="completed"):
        self.balance += int(amount)
        self.save()
        self._make_transaction(amount, user, for_package, status)

    def _make_transaction(
        self, amount, user, for_package=False, tnx_type="deposit", status="pending"
    ):
        tnx = Transactions(
            transaction_type=tnx_type,
            user=user,
            amount=int(amount),
            status=status,
            for_package=for_package,
        )
        tnx.save()

    @transaction.atomic()
    def do_withdrawal(self, amount, user, for_package=False, status="pending"):
        try:
            int(amount)
        except TypeError:
            raise ValidationError(
                message=FAILURE_MESSAGES["enter_valid_amount"], code=400
            )
        if self.balance < 100:
            raise ValidationError(message=FAILURE_MESSAGES["funds_too_low"], code=400)
        if int(amount) <= int(self.balance):
            self.balance -= amount
            self._make_transaction(amount, user, for_package, "withdrawal", status)
            self.save()
            return

        raise ValidationError(message=FAILURE_MESSAGES["insufficient_funds"], code=400)

    @property
    def total_withrawals(self):
        return self._get_transaction_total("withdrawal")

    @property
    def total_deposits(self):
        return self._get_transaction_total("deposit")

    def latest_transactions(self):
        # print this with .query to view the sql
        return self.user.transactions.all().order_by("-id")[0:5]

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
    minimum_amount = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, validators=[validate_number]
    )
    maximum_amount = models.DecimalField(
        default=0, decimal_places=2, max_digits=12, validators=[validate_number]
    )
    return_on_investmentent = models.PositiveIntegerField()
    codename = models.CharField(max_length=30, unique=True)
    days = models.PositiveIntegerField(validators=[validate_number])
    level = models.CharField(choices=PACKGE_CHOICES, default="silver", max_length=30)
    active = models.BooleanField(default=True)

    @property
    def is_new(self):
        return (self.created_at - datetime.datetime.now().date()).days < 60

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        snakeised_codename = pattern.sub("_", self.name).lower()
        pkg = Package.objects.filter(codename=snakeised_codename)
        if pkg:
            self.codename = snakeised_codename + "_{}".format(pkg.count() + 1)
        else:
            self.codename = snakeised_codename
        super(Package, self).save(**kwargs)


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
]


class Investment(DirtyFieldsMixin, TimeStampMixin):
    amount = models.DecimalField(default=0, decimal_places=2, max_digits=12)
    package = models.ForeignKey(Package, on_delete=models.DO_NOTHING)
    status = models.CharField(
        choices=INVESTMENT_STATUS, max_length=20, default="pending"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return "{} for package: {}".format(
            intcomma(floatformat(self.amount)), self.package
        )

    @property
    def total_roi(self):
        return self.roischedule_set.aggregate(Sum("roi_amount"))["roi_amount__sum"] or 0

    @property
    def total_roi_paid(self):
        # roi_amount__sum default key generated by the aggrefate fn
        return (
            self.roischedule_set.filter(status="transferred").aggregate(
                Sum("roi_amount")
            )["roi_amount__sum"]
            or 0
        )

    @property
    def total_roi_left(self):
        # roi_amount__sum default key generated by the aggrefate fn
        return (
            self.roischedule_set.filter(~Q(status="transferred")).aggregate(
                Sum("roi_amount")
            )["roi_amount__sum"]
            or 0
        )

    @property
    def next_payment_date(self):
        return (
            self.roischedule_set.exclude(Q(status="completed") | Q(status="transfer"))
            .order_by("maturity_date")
            .values_list("maturity_date", flat=True)
            .first()
        )

    def period_in_days(self):
        return (
            (self.next_payment_date - datetime.datetime.now().date()).days
            if self.next_payment_date
            else 0
        )

    def get_roi_schedules(self):
        return self.roischedule_set.order_by("maturity_date")


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

    def __str__(self):
        return "Roi amount: {} status: {}".format(self.roi_amount, self.status)
