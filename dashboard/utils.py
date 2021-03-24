from __future__ import absolute_import

import requests
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse

from finance.forms import BankForm
from finance.models import Bank, Transactions
from paytime import settings
from paytime.utils import FAILURE_MESSAGES, SUCCESS_MESSAGES
from user.forms import ProfileForm


def set_pagination_data(queryset, request):
    """
    Set the pagination data to be used

    Args:
        queryset: The queryset to be paginated
        request: The request object
    """
    page = request.GET.get("page", 1)
    paginator = Paginator(queryset, 7)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    return queryset


class ProfileFormMixin:
    def _set_bank_form_data(self, bank, account_number):
        return {"bank": bank, "account_number": account_number}

    def _set_profile_form(self, user, use_form=False):
        # returns the intial value of the user's
        # profile details on load
        data = {
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
        if use_form:
            return ProfileForm(initial={**data})
        return data

    def _set_profile_context(self, profile_form, request, user):
        try:
            bank = Bank.objects.get(user=user)
            # set the intial value/upon load, the value of the user's
            # bank details
            bank_form = BankForm(
                initial={**self._set_bank_form_data(bank, bank.account_number)}
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


class ProcessRequestMixin:
    headers = {"Authorization": "Bearer {}".format(settings.PAYSTACK_SECRET_KEY)}
    base_url = "https://api.paystack.co/"

    def _request(self, method, resource_url, **kwargs):
        """
        private method to access urls with payload if available

        Args:
            method: request http method
            resource_url: the resource endpoint
            kwargs: keyword args

        Returns:
            JSON respnse
            status code: http status code
        """

        qs = kwargs.get("qs")
        response = method(
            self.base_url + resource_url, json=kwargs, headers=self.headers, params=qs
        )
        return response.json(), response.status_code

    def _initiate_transfer_payload(self, amount, recipient_code):
        """Set the payload for initiate transfer (paystack)"""
        return {
            "source": "balance",
            "reason": "payment_request",
            "amount": amount,
            "recipient": recipient_code,
        }

    def _get_transfer_recipient_payload(self, fullname, acct_num, bank_code):
        return {
            "type": "nuban",
            "name": fullname,
            "account_number": acct_num,
            "bank_code": bank_code,
        }

    def _json_error_response(self, message, status=400):
        return JsonResponse(
            {"success": False, "error": True, "message": message}, status=status
        )

    def _json_success_response(self, message):
        return JsonResponse({"success": True, "error": False, "message": message})

    def _get_transfer_recipient(self, method, user):
        """Gets the transfer recipient code

        Gets the recipient code to be used in
        making transfers for a particular user
        it is advisible to store this code in the
        db, corresponding to the said user

        Args:
            self: instance
            method: http method
            user: user object

        Returns:
            recipient_code: The recipient code
            status_code: http status code
            json_response: response object

        """
        json_response, status_code = self._request(
            method,
            "transferrecipient",
            **self._get_transfer_recipient_payload(
                user.get_full_name(),
                user.bank.account_number,
                user.bank.bank_detail.code,
            )
        )
        recipient_code = json_response.get("data").get("recipient_code")
        return recipient_code, status_code, json_response.get("message")

    def _save_user_recipient_code(self, method, user):
        """Save the user's recipient code in the db

        Saves the user's recipient code corresponding to
        the user's bank details

        Args:
            self: instance
            method: http method
            user: user object
        """
        recipient_code, status_code, msg = self._get_transfer_recipient(method, user)

        if status_code >= 400:
            return self._json_error_response(msg)
        user.bank.recipient_code = recipient_code
        user.bank.save()

    def _initiate_transfer_request(self, method, amount, recipient_code):
        json_response, status_code = self._request(
            method,
            "transfer",
            # convert from kobo to Naira
            **self._initiate_transfer_payload(int(amount) * 100, recipient_code)
        )
        return json_response, status_code

    def _process_payment(self, payment_id):
        """
        Process transfer payment to user' account

        Args:
            payment_id(str): The payment id for implementing transfer

        Returns:
             Json response
        """

        try:
            int(payment_id)
        except (TypeError, ValueError):
            raise ValidationError(FAILURE_MESSAGES["invalid"].format("Payment Id"))

        # get the payment
        txn = Transactions.objects.get(id=payment_id)
        user = txn.user
        if not user.recipient_code:
            # TODO we need to first validate the account number
            # but also we may skip this validation by validating the account number
            # the user saves
            # save user recipient code in db
            self._save_user_recipient_code(requests.post, user)
        # if the user already has a recepient code, then
        # just initiate transfer with the recepient code
        json_response, status_code = self._initiate_transfer_request(
            requests.post, txn.amount, user.recipient_code
        )

        if status_code >= 400:
            raise ValidationError(json_response.get("message"))

        transfer_code = json_response["data"]["transfer_code"]
        json_response, _ = self._request(
            requests.post, "transfer/finalize_transfer", transfer_code=transfer_code
        )

        # Disable Transfers OTP from here
        # https://dashboard.paystack.com/#/settings/preferences
        # uncheck Confirm transfers before sending
        # or it can also be done via postman
        try:
            if json_response["message"] == SUCCESS_MESSAGES["no_otp_transfer"]:
                # successful because our payment doesn't need OTP
                # but it returns a 400 status code
                txn.status = "completed"
                txn.save()
                # messages.success(request, json_response.get("message"))
                return self._json_success_response(
                    SUCCESS_MESSAGES["blank_successful"].format("Transfer")
                )
        except AttributeError:
            raise ValidationError(FAILURE_MESSAGES["something_went_wrong"])


class OnlyAdminAccessMixin(UserPassesTestMixin):
    """Test to determin if the user is an admin

    Inheriting classes should always inherit LoginRequiredMixin
    before inheriting this class
    """

    def test_func(self):
        return self.request.user.is_staff
