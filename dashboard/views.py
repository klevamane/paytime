from __future__ import absolute_import

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.shortcuts import redirect, render
from django.views import View

from finance.forms import BankForm
from finance.models import Bank
from paytime.utils import FAILURE_MESSAGES, SUCCESS_MESSAGES
from user.forms import ProfileForm
from user.models import User


def users_list(request):
    return render(request, "dashboard/users-list.html")


@login_required
def dashboard_data(request):
    return render(request, "dashboard/users-list.html")


class BankDetailsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/add-bank-details.html",
            context={"form": BankForm(), "view_path": request.path.rsplit("/")[2]},
        )

    def post(self, request):
        form = BankForm(data=request.POST)
        if Bank.objects.filter(user_id=request.user.id).exists():
            messages.error(request, FAILURE_MESSAGES["cannot_add_multiple_bank"])
            return render(
                request,
                template_name="dashboard/add-bank-details.html",
                context={"form": form},
            )
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = instance.user = request.user
            instance.save()
            messages.success(request, SUCCESS_MESSAGES["bank_account_added"])
            return redirect("dashboard-home")
        return render(
            request,
            template_name="dashboard/add-bank-details.html",
            context={"form": form},
        )


class BankUpdateView(LoginRequiredMixin, View):
    def post(self, request):
        instance = Bank.objects.get(user_id=request.user.id)
        if not instance.can_update:
            messages.error(request, FAILURE_MESSAGES["cannot_update_bank"])
            return render(
                request,
                template_name="dashboard/update-bank-details.html",
                context={"form": BankForm()},
            )
        form = BankForm(data=request.POST, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = instance.user = request.user
            instance.save()
            messages.success(request, SUCCESS_MESSAGES["bank_account_updated"])
            return render(
                request,
                template_name="dashboard/update-bank-details.html",
                context={"form": BankForm()},
            )
        return render(
            request,
            template_name="dashboard/update-bank-details.html",
            context={"form": form},
        )

    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/update-bank-details.html",
            context={"form": BankForm(), "view_path": request.path.rsplit("/")[2]},
        )


class DocumentView(View):
    def get(self, request):
        return render(request=request, template_name="dashboard/profile/documents.html")


class DepositView(View):
    def get(self, request):
        return render(
            request=request, template_name="dashboard/transactions/deposit.html"
        )


class WithdrawalView(View):
    def get(self, request):
        return render(
            request=request, template_name="dashboard/transactions/withrawal.html"
        )


class TransactionsAllView(View):
    def get(self, request):
        return render(request=request, template_name="dashboard/transactions/all.html")


class WalletView(View):
    def get(self, request):
        return render(request=request, template_name="dashboard/wallet/wallet.html")


class InvestView(View):
    def get(self, request):
        return render(request, "dashboard/invest/invest.html")


class InvestmentsView(View):
    def get(self, request):
        return render(request, "dashboard/invest/investments.html")


class InvestmentDetailView(View):
    def get(self, request):
        return render(request, "dashboard/invest/detail.html")


class PaymentView(View):
    def get(self, request):
        return render(request, "dashboard/invest/payment.html")


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        profile_form = self._set_profile_form(user)
        try:
            bank = Bank.objects.get(user=user)
            bank_form = BankForm(
                initial={"bank": bank.bank, "account_number": bank.account_number}
            )
        except Bank.DoesNotExist:
            bank_form = BankForm()
        context = {"profile_form": profile_form, "bank_form": bank_form}
        return render(
            request, template_name="dashboard/profile/profile.html", context=context
        )

    def _set_profile_form(self, user):
        # returns the intial value/upon load, the value of the user's
        # profile details
        return ProfileForm(
            initial={
                "firstname": user.firstname,
                "lastname": user.lastname,
                "address1": user.address1,
                "area": user.area,
                "email": user.email,
                "city": user.city,
                "state": user.state,
                "mobile": user.mobile,
                "date_of_birth": user.date_of_birth,
            }
        )


class HandleProfileSubmit(ProfileView, View):
    def post(self, request):
        user = User.objects.get(id=request.user.id)
        profile_form = ProfileForm(request.POST, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Save successfull")
            return redirect("profile")
        # this ensures that whenever error(s) are displayed in the template
        # the bank form still retains its form displayed
        # else the form shows none because it can access a bank form from the context
        # this issue occurs because we a rerendering the page,
        # if we redirect to the page, then we don't need to bother about this issue,
        # but then again, we would loose the form errors
        # perhaps we can make use of messages, ie putting the errors in messages will
        # help us avoid this
        # but we currently want to show the errors withing the template input itself
        try:
            bank = Bank.objects.get(user=user)
            # set the intial value/upon load, the value of the user's
            # bank details
            bank_form = BankForm(
                initial={"bank": bank.bank, "account_number": bank.account_number}
            )
        except Bank.DoesNotExist:
            bank_form = BankForm()
        context = {"profile_form": profile_form, "bank_form": bank_form}
        return render(
            request, template_name="dashboard/profile/profile.html", context=context
        )


class HandleBankSubmit(ProfileView, View):
    def post(self, request):
        data = request.POST.dict()
        if "user" in data:
            # we don't want a user to
            # be able do update this
            del data["user"]
        if "can_update" in data:
            del data["can_update"]
        data["user"] = request.user
        # set this so the user isn't able to update
        # in future
        data["can_update"] = False

        try:
            # update
            bank = Bank.objects.get(user=request.user)
            bank_form = BankForm(data, instance=bank)
            if not bank.can_update:
                bank_form.errors["account_number"] = FAILURE_MESSAGES[
                    "cannot_update_bank"
                ]
                messages.error(request, FAILURE_MESSAGES["cannot_update_bank"])
        except Bank.DoesNotExist:
            # create
            bank_form = BankForm(data)
        if bank_form.is_valid():
            bank_form.save()
            messages.success(request, "Save successfull")
            return redirect("profile")

        user = User.objects.get(id=request.user.id)
        profile_form = self._set_profile_form(user)
        return render(
            request,
            "dashboard/profile/profile.html",
            {"bank_form": bank_form, "profile_form": profile_form},
        )
