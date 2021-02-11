from __future__ import absolute_import

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse

from paytime import settings
from user.forms import ProfileForm


def set_pagination_data(queryset, request):
    """
    Set the pagination data to be used

    Args:
        queryset: The queryset to be parginate
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
    def _set_bank_form(self, bank, account_number):
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
            JSON respnse, status code
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

    def _get_txfr_recipient_payload(self, fullname, acct_num, bank_code):
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
        json_response, status_code = self._request(
            method,
            "transferrecipient",
            **self._get_txfr_recipient_payload(
                user.get_full_name(),
                user.bank.account_number,
                user.bank.bank_detail.code,
            )
        )
        recipient_code = json_response.get("data").get("recipient_code")
        return recipient_code, status_code, json_response.get("message")

    def _save_user_recipient_code(self, method, user):
        recipient_code, status_code, msg = self._get_transfer_recipient(method, user)

        if status_code >= 400:
            return self._json_error_response(msg)
        user.bank.recipient_code = recipient_code
        user.bank.save()
