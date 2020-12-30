from __future__ import absolute_import

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.forms.utils import ErrorList
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import resolve, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from pypaystack import Transaction

from dashboard.forms import PaymentForm
from finance.forms import BankForm
from finance.models import Bank, Investment, Package, Wallet
from paytime import settings
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
            request=request,
            template_name="dashboard/transactions/deposit.html",
            context={
                "fullname": request.user.get_full_name(),
            },
        )


class WithdrawalView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/transactions/withrawal.html",
            context={"fullname": request.user.get_full_name()},
        )


class TransactionsAllView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/transactions/all.html",
            context={"fullname": request.user.get_full_name()},
        )


class WalletView(View):
    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/wallet/wallet.html",
            context={"fullname": request.user.get_full_name()},
        )


class InvestView(View):
    def get(self, request):
        return render(
            request,
            "dashboard/invest/invest.html",
            context={"fullname": request.user.get_full_name()},
        )


class InvestmentsView(View):
    def get(self, request):
        # get user investments
        context = {}

        user_investments_qs = Investment.objects.filter(user=request.user)
        if user_investments_qs:
            last_investment = user_investments_qs.last()
            context["last_investment"] = last_investment
        page = request.GET.get("page", 1)
        paginator = Paginator(user_investments_qs, 5)
        try:
            investments = paginator.page(page)
        except PageNotAnInteger:
            investments = paginator.page(1)
        except EmptyPage:
            investments = paginator.page(paginator.num_pages)

        # this is important that we use update instead of manually assigning key, value

        context.update(
            {"user_investments": investments, "fullname": request.user.get_full_name()}
        )
        return render(request, "dashboard/invest/investments.html", context=context)


class InvestmentDetailView(View):
    def get(self, request, id):
        return render(
            request,
            "dashboard/invest/detail.html",
            context={"fullname": request.user.get_full_name()},
        )


class PaymentVerificationView(View):
    def post(self, request):
        try:
            amount, pkg, reference_id = list((json.loads(request.body)).values())
        except ValueError:
            # not enough values to unpack
            # return an invalid response
            return
            pass
        transaction = Transaction(authorization_key=settings.PAYSTACK_SECRET_KEY)
        response = transaction.verify(reference_id)
        if response[0] == 200:
            verify_amount = response[3]["amount"] / 100
            # check that the amount paid to paystack
            # was the amount that was
            if verify_amount == int(amount):
                # create an investment plan for the user
                # redirect to the investment page
                package = Investment(
                    amount=amount,
                    package=Package.objects.get(codename=pkg),
                    user=request.user,
                )
                package.save()
                resolved_url = reverse("investments_view_url")
                return JsonResponse({"resolved_url": resolved_url}, safe=False)
            # return error to the user indicating that there has been
            # an amount mismatch therefore the amount has been added to the users
            # get or create a user wallet
            user_wallet, _ = Wallet.objects.get_or_create(user=request.user)
            user_wallet.do_depost(amount, request.user)
            messages.info(
                request,
                "We experienced an amount mismatch, we have instead updated your wallet",
            )
            resolved_url = reverse("wallet_url")
            return JsonResponse({"resolved_url": resolved_url}, safe=False)
        return JsonResponse(
            {"message": "Transaction not completed unable to verify transaction"},
            safe=False,
        )


class PaymentView(View):
    def get(self, request):
        try:
            package = Package.objects.get(codename=request.GET.get("codename"))
        except Package.DoesNotExist:
            package = None
        if package:
            payment_form = PaymentForm(initial={"package": package})
        else:
            payment_form = PaymentForm()
        return render(
            request,
            "dashboard/invest/payment.html",
            context={
                "payment_form": payment_form,
                "email": request.user.email,
                "firstname": request.user.firstname,
                "lastname": request.user.lastname,
                "paystatck_pub_key": settings.PAYSTACK_PUBLIC_KEY,
            },
        )


def validate_package_amount(request):
    data = json.loads(request.body)
    payment_form = PaymentForm(data=data)
    if payment_form.errors:
        return JsonResponse({**payment_form.errors}, status=400)
    return JsonResponse({}, status=200)


class PaystackView(View):
    def get(self, request):
        pass

    def post(self, request):
        pass


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
        context = {
            "profile_form": profile_form,
            "bank_form": bank_form,
            "fullname": request.user.get_full_name(),
        }
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
            return redirect("profile_url")
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
        context = {
            "profile_form": profile_form,
            "bank_form": bank_form,
            "fullname": request.user.get_full_name(),
        }
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
            return redirect("profile_url")

        user = User.objects.get(id=request.user.id)
        profile_form = self._set_profile_form(user)
        return render(
            request,
            "dashboard/profile/profile.html",
            {
                "bank_form": bank_form,
                "profile_form": profile_form,
                "fullname": request.user.get_full_name(),
            },
        )
