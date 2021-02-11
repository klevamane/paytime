from __future__ import absolute_import

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse

from paytime import settings


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
            returns json respnse, status code
        """

        qs = kwargs.get("qs")
        response = method(
            self.base_url + resource_url, json=kwargs, headers=self.headers, params=qs
        )
        return response.json(), response.status_code

    def _initiate_transfer_payload(self, amount, recipient_code):
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
