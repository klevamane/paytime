from __future__ import absolute_import

import datetime
import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.forms.utils import ErrorList
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from dashboard.forms import PaymentForm
from finance.forms import BankForm
from finance.models import Bank, Investment, Package, RoiSchedule, Transactions, Wallet
from paytime import settings
from paytime.utils import FAILURE_MESSAGES, SUCCESS_MESSAGES
from user.forms import DocumentForm, ProfileForm
from user.models import Document, User


def users_list(request):
    return render(request, "dashboard/users-list.html")


@login_required
def dashboard_data(request):
    return render(request, "dashboard/users-list.html")


DOCUMENT_FILE_TYPES = ["png", "jpg", "jpeg", "pdf"]


class DocumentView(LoginRequiredMixin, View):
    def get(self, request):
        form = DocumentForm()
        try:
            document = Document.objects.get(user=request.user)
        except Document.DoesNotExist:
            document = None
        return render(
            request=request,
            template_name="dashboard/profile/documents.html",
            context={
                "document": document,
                "form": form,
                "fullname": request.user.get_full_name(),
            },
        )

    def post(self, request):
        user_document = None
        try:
            user_document = Document.objects.get(user=request.user)
            form = DocumentForm(request.POST, request.FILES, instance=user_document)
        except Document.DoesNotExist:
            form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            file = request.FILES["file"]
            error = None
            file_type = None
            try:
                file_type = file.name.split(".")[-1].lower()
            except IndexError:
                error = True
            if file_type not in DOCUMENT_FILE_TYPES or error:
                messages.error(
                    request,
                    "The file type is not supported, kindly upload a supported file",
                )
                # add document to document form on post to enable the posted page extract the document data
                return render(
                    request=request,
                    template_name="dashboard/profile/documents.html",
                    context={
                        "document": user_document if user_document else instance,
                        "form": form,
                        "fullname": request.user.get_full_name(),
                    },
                )

            instance.save()
            messages.success(request, "Document uploaded successfully")
            return render(
                request=request,
                template_name="dashboard/profile/documents.html",
                context={
                    "document": user_document if user_document else instance,
                    "form": form,
                    "fullname": request.user.get_full_name(),
                },
            )


class DepositView(LoginRequiredMixin, View):
    def get(self, request):
        tnxs = Transactions.objects.filter(
            user_id=request.user.id, transaction_type="deposit"
        )
        return render(
            request=request,
            template_name="dashboard/transactions/deposit.html",
            context={
                "fullname": request.user.get_full_name(),
                "transactions": tnxs if tnxs else None,
            },
        )


class WithdrawalView(LoginRequiredMixin, View):
    def get(self, request):
        tnxs = Transactions.objects.filter(
            user_id=request.user.id, transaction_type="withdrawal"
        )
        return render(
            request=request,
            template_name="dashboard/transactions/withrawal.html",
            context={
                "fullname": request.user.get_full_name(),
                "transactions": tnxs if tnxs else None,
            },
        )


class TransactionsAllView(LoginRequiredMixin, View):
    def get(self, request):
        tnxs = Transactions.objects.filter(user_id=request.user.id)
        return render(
            request=request,
            template_name="dashboard/transactions/all.html",
            context={
                "fullname": request.user.get_full_name(),
                "transactions": tnxs if tnxs else None,
            },
        )


class WalletView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/wallet/wallet.html",
            context={"fullname": request.user.get_full_name()},
        )


class InvestView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "dashboard/invest/invest.html",
            context={"fullname": request.user.get_full_name()},
        )


class InvestmentsView(LoginRequiredMixin, View):
    def get(self, request):
        # get user investments
        context = {}

        user_investments_qs = Investment.objects.filter(user=request.user).order_by(
            "-id"
        )
        if user_investments_qs:
            last_investment = user_investments_qs.latest("id")
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


class InvestmentDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        # get the investment by Id
        # get the ROI Schedule of the particular investment
        # not these can only be done if the investment exists
        # and belongs to the current user
        try:
            investment = Investment.objects.get(id=id, user_id=request.user.id)
        except Investment.DoesNotExist:
            raise Http404
        # roi_amount__sum default key generated by the aggrefate fn
        total_roi = investment.roischedule_set.aggregate(Sum("roi_amount"))[
            "roi_amount__sum"
        ]
        # it is expected that for every investment created
        # there should be it's roi_schedule_set also created
        # but we still need to check for safety here
        if investment.roischedule_set.count() == 0:
            return HttpResponseForbidden()
        total_roi_paid = investment.roischedule_set.filter(
            status="completed"
        ).aggregate(Sum("roi_amount"))["roi_amount__sum"]
        # get the next ROI payment date
        next_payment_date = (
            investment.roischedule_set.exclude(
                Q(status="completed") | Q(status="transfer")
            )
            .order_by("maturity_date")
            .values_list("maturity_date", flat=True)
            .first()
        )

        return render(
            request,
            "dashboard/invest/detail.html",
            context={
                "fullname": request.user.get_full_name(),
                "investment": investment,
                "roi_schedules": investment.roischedule_set.order_by("maturity_date"),
                "total_roi": total_roi,
                "total_roi_paid": total_roi_paid or 0,
                "total_roi_left": total_roi - (total_roi_paid or 0),
                "next_payment_date": next_payment_date
                if next_payment_date is not None
                else "Completed",
                "period": (next_payment_date - datetime.datetime.now().date()).days
                if next_payment_date
                else 0,
            },
        )


class TransferToWalletView(View):
    # get roi
    # check that user owns the investment
    # check that the status is payable to user
    # if so deposit to the wallet
    # update the status of the ROI to transfer completed
    # if the ROI is the ROI with the last date (maturity date)?
    # mark all ROIs in that investment as completed
    # wait already paid ROIs ought to have been marked completed

    # instead, mark the investment as completed
    # therefore during withrawals or performing investment actions
    # we need to check if the investment has beeen completed first
    def get(self, request, roi_id):

        try:
            roi = RoiSchedule.objects.get(
                id=roi_id, investment__user=request.user, status="transfer"
            )
        except (RoiSchedule.DoesNotExist, ValueError):
            raise Http404("Operation unsuccessful")

        # Never use try catch block in the transaction block
        with transaction.atomic():
            user_wallet, _ = Wallet.objects.get_or_create(user=request.user)
            roi.status = "completed"
            roi.save()
            user_wallet.do_depost(roi.roi_amount, request.user)
            ids_to_update = [roi.id]
            # check if this is the last ROI of the investment
            # if so set the investment status to completed
            if roi.investment.roischedule_set.order_by("-maturity_date").first() == roi:
                # go through each roi of the particular investment
                # and check that it's status is completed
                # before setting the investment and the last (ROI) to completed
                # because there might be a case where by
                # first roi is ready to be paid to the wallet
                # as well as the second one (assume that this is the last)
                # if we go and just check if the invest this is the last one
                # and complete the investment, it'll mean that something will be wrong

                # one way to make this work is
                #  we can go request that the other roi be paid first
                # into the wallet
                # or we just move every other ROI
                # of this investment into the wallet.

                # it is expected that their status be (ready to be transferred (ie "transfer")
                # but we are just checking still to be sure

                for r in roi.investment.roischedule_set.all():
                    # since the current ROI has already been paid
                    # it won't be checked within this loop
                    if r.status == "transfer":
                        r.status = "completed"
                        r.save()
                        user_wallet.do_depost(r.roi_amount, request.user)
                        ids_to_update.append(r.id)

                # make the investment status as completed
                roi.investment.status = "completed"
                roi.investment.save()

                # The last ROI is paid with the capital
                user_wallet.do_depost(roi.investment.amount, request.user)
            dic = {}
            dic.update({"idsToUpdate": ids_to_update})
            return JsonResponse(dic, safe=False)


class PaymentVerificationView(View):
    def post(self, request):
        try:
            amount, pkg, reference_id = list((json.loads(request.body)).values())
        except ValueError:
            # not enough values to unpack
            # return an invalid response
            return

        headers = {"Authorization": "Bearer {}".format(settings.PAYSTACK_SECRET_KEY)}
        paystack_verify_url = "https://api.paystack.co/transaction/verify/{}".format(
            reference_id
        )
        response = requests.get(url=paystack_verify_url, headers=headers)

        if response.status_code == 200:
            user_wallet, _ = Wallet.objects.get_or_create(user=request.user)
            verify_amount = response.json()["data"]["amount"] / 100
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
                # the client should be able to redirect to the
                # desired page using this url
                resolved_url = reverse("investments_view_url")
                user_wallet.do_depost(amount, request.user, True)
                return JsonResponse({"resolved_url": resolved_url}, safe=False)

            else:
                # return error to the user indicating that there has been
                # an amount mismatch therefore the amount has been added to the user's wallet
                # get or create a user wallet
                user_wallet.do_depost(amount, request.user)
                messages.info(
                    request,
                    "We experienced an amount mismatch, we have instead updated your wallet",
                )
                resolved_url = reverse("wallet_url")
            # add to transaction table as deposit
            # type package,
            # would the user be allowed to directly deposit into their wallet?
            return JsonResponse({"resolved_url": resolved_url}, safe=False)
        return JsonResponse(
            {"message": "Transaction not completed unable to verify transaction"},
            safe=False,
            status=400,
        )


class PaymentView(LoginRequiredMixin, View):
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
                "fullname": request.user.get_full_name(),
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
        # disable email field to prevent subsequent edits
        profile_form.fields["email"].disabled = True
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
        data = request.POST.copy()
        # ensures that the email field is not updated
        data["email"] = user.email
        profile_form = ProfileForm(data, instance=user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Save successful")
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
            messages.success(request, "Save successful")
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
