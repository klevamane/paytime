from __future__ import absolute_import

import json

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.forms.utils import ErrorList
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from dashboard.forms import MessageForm, PaymentForm
from dashboard.models import MessageCenter
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
        try:
            document = Document.objects.get(user=request.user)
        except Document.DoesNotExist:
            document = None
        return render(
            request=request,
            template_name="dashboard/profile/documents.html",
            context={
                "document": document,
                "form": DocumentForm(),
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
            # use get to avoid MultiValueDictKeyError
            file = request.FILES.get("file")
            error = None
            file_type = None
            try:
                file_type = file.name.split(".")[-1].lower()
            except (IndexError, AttributeError):
                error = True
            if file_type not in DOCUMENT_FILE_TYPES or error:
                messages.error(
                    request,
                    "The file type is not supported, kindly upload a supported file",
                )
                return self._render_profile_document(
                    form, instance, request, user_document
                )
            if (file.size / 1024) > 601:
                messages.error(request, "The file size must be less or equal to 600KB")
                return self._render_profile_document(
                    form, instance, request, user_document
                )

            instance.save()
            messages.success(request, "Document uploaded successfully")
            return self._render_profile_document(form, instance, request, user_document)

    def _render_profile_document(self, form, instance, request, user_document):
        return render(
            request=request,
            template_name="dashboard/profile/documents.html",
            context={
                "document": user_document if user_document else instance,
                "form": form,
                "profile_picture_url": request.user.profile_picture.url,
            },
        )


class TransactionsAllView(LoginRequiredMixin, ListView):
    qry = {}

    model = Transactions
    template_name = "dashboard/transactions/all.html"
    paginate_by = 5
    context_object_name = "transactions"

    def get_queryset(self):
        return Transactions.objects.filter(
            user_id=self.request.user.id, **self.qry
        ).order_by("-id")


class DepositView(TransactionsAllView):
    qry = {"transaction_type": "deposit"}
    template_name = "dashboard/transactions/deposit.html"


class WithdrawalView(TransactionsAllView):
    qry = {"transaction_type": "withdrawal"}
    template_name = "dashboard/transactions/withrawal.html"


class WalletView(LoginRequiredMixin, View):
    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return render(
            request=request,
            template_name="dashboard/wallet/wallet.html",
            context={
                "wallet": wallet,
                "roi_gain": wallet.total_withrawals - wallet.total_deposits,
            },
        )

    def post(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        try:
            wallet.do_withdrawal(wallet.balance, request.user)
            messages.success(
                request, SUCCESS_MESSAGES["operation_successful"].format("withdrawal")
            )
        except ValidationError as e:
            messages.error(request, e.messages[0])
        return render(
            request=request,
            template_name="dashboard/wallet/wallet.html",
            context={
                "wallet": wallet,
                "roi_gain": wallet.total_withrawals - wallet.total_deposits,
            },
        )


class InvestView(LoginRequiredMixin, View):
    packages = Package.objects.all()

    def get(self, request):
        return render(
            request,
            "dashboard/invest/invest.html",
            context={
                "packages": self.packages,
            },
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
        # there seem to be an issue an issue we noticed by simply assigning the data
        # by dict["key"] = value
        context.update({"user_investments": investments})
        return render(request, "dashboard/invest/investments.html", context=context)


class InvestmentDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        try:
            investment = Investment.objects.get(id=id, user_id=request.user.id)
        except Investment.DoesNotExist:
            raise Http404

        # it is expected that for every investment created
        # there should be it's roi_schedule_set also created
        # but we still need to check for safety here
        if investment.roischedule_set.count() == 0:
            return HttpResponseForbidden()

        return render(
            request,
            "dashboard/invest/detail.html",
            context={
                "investment": investment,
                "next_payment_date": investment.next_payment_date
                if investment.next_payment_date is not None
                else "Completed",
            },
        )


class TransferToWalletView(View):
    # get roi
    # check that user owns the investment
    # check that the status is payable to user
    # if so deposit to the wallet
    # update the status of the ROI from transfer to completed
    # if the ROI is the ROI with the last date (maturity date)?
    # mark all ROIs in that investment as completed

    # Wait! already paid ROIs ought to have been marked completed
    # anyways still mark

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
                #  we can ensure that the other rois be paid first
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
        # check if user already has an active investment
        # a user having an active investment shouldn't be able
        # to make any other payment

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
            {"message": FAILURE_MESSAGES["incomplete_unverifiable_tnx"]},
            safe=False,
            status=400,
        )


class PaymentView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.has_active_investment:
            messages.error(request, FAILURE_MESSAGES["user_has_active_investment"])
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


@login_required
def validate_package_amount(request):

    if request.user.has_active_investment:
        response = {
            "success": False,
            "message": FAILURE_MESSAGES["user_has_active_investment"],
        }
        return JsonResponse(data=response, status=400)

    data = json.loads(request.body)
    payment_form = PaymentForm(data=data)
    if payment_form.errors:
        return JsonResponse({**payment_form.errors}, status=400)
    return JsonResponse({}, status=200)


class PackageDetail(LoginRequiredMixin, View):
    """Returns AJAX data"""

    def get(self, request, codename):
        try:
            package = Package.objects.get(codename=codename)
        except (Package.DoesNotExist, AttributeError, ValueError):
            return JsonResponse(data=None, status=400, safe=False)

        data = {
            "duration": package.days,
            "roi": package.return_on_investmentent,
            "minimum_amount": intcomma(floatformat(package.minimum_amount)),
            "maximum_amount": intcomma(floatformat(package.maximum_amount)),
        }
        return JsonResponse(data=data, status=200, safe=False)


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        profile_form = self._set_profile_form(user)
        # disable email field to prevent subsequent edits
        profile_form.fields["email"].disabled = True
        context = self._set_profile_context(profile_form, request, user)
        return render(
            request, template_name="dashboard/profile/profile.html", context=context
        )

    def _set_profile_context(self, profile_form, request, user):
        try:
            bank = Bank.objects.get(user=user)
            # set the intial value/upon load, the value of the user's
            # bank details
            bank_form = BankForm(
                initial={"bank": bank.bank, "account_number": bank.account_number}
            )
        except Bank.DoesNotExist:
            bank_form = BankForm()
        return {
            "profile_form": profile_form,
            "bank_form": bank_form,
            "profile_picture_url": request.user.profile_picture.url
            if request.user.profile_picture
            else "",
        }

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
                "gender": user.gender,
                # "profile_picture": None
            }
        )


class MessageView(LoginRequiredMixin, View):
    template_name = "dashboard/messages/detail.html"
    model = MessageCenter

    def get_queryset(self):
        return MessageCenter.objects.filter(to=self.request.user)


class MessageInboxDetail(MessageView, DetailView):
    template_name = "dashboard/messages/detail.html"
    model = MessageCenter

    def get_queryset(self):
        return self.request.user.messages


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "dashboard/messagecenter_confirm_delete.html"
    model = MessageCenter

    def get_success_url(self):
        return reverse("message_inbox_view_url")


class MessageInboxList(MessageView, ListView):
    template_name = "dashboard/messages/inbox.html"
    ordering = ["-created_at"]
    paginate_by = 4


class MessageSentListView(MessageInboxList):
    template_name = "dashboard/messages/sent.html"

    def get_queryset(self):
        return MessageCenter.objects.filter(sender=self.request.user).order_by("-id")


class MessageCreateView(MessageView, CreateView):
    template_name = "dashboard/messages/create.html"
    model = MessageCenter
    form_class = MessageForm

    def get_success_url(self):
        messages.success(self.request, SUCCESS_MESSAGES["msg_sent_to_admin"])
        # we would lazily reverse if done withing the class as
        # oppsose to this method
        # see https://stackoverflow.com/questions/48669514/difference-between-reverse-and-reverse-lazy-in-django
        return reverse("message_inbox_view_url")

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)


class HandleProfileSubmit(ProfileView, View):
    def post(self, request):
        user = User.objects.get(id=request.user.id)
        data = request.POST.copy()
        # ensures that the email field is not updated
        data["email"] = user.email
        profile_form = ProfileForm(data, files=request.FILES, instance=user)
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
        context = self._set_profile_context(profile_form, request, user)
        return render(
            request, template_name="dashboard/profile/profile.html", context=context
        )


class HandleBankSubmit(ProfileView, View):
    def post(self, request):
        data = request.POST.dict()

        # we don't want a user to
        # be able do update this
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

        for k, err in bank_form.errors.items():
            messages.error(request, err[0])
        user = User.objects.get(id=request.user.id)
        profile_form = self._set_profile_form(user)
        return render(
            request,
            "dashboard/profile/profile.html",
            {
                "bank_form": bank_form,
                "profile_form": profile_form,
                "profile_picture_url": request.user.profile_picture.url
                if request.user.profile_picture
                else "",
            },
        )
