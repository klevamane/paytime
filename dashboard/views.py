from __future__ import absolute_import

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from finance.forms import BankForm
from paytime.utils import SUCCESS_MESSAGES


def users_list(request):
    return render(request, "dashboard/users-list.html")


@login_required
def dashboard_data(request):
    return render(request, "dashboard/users-list.html")


class BankDetailsView(LoginRequiredMixin, View):
    def post(self, request):
        form = BankForm(data=request.POST)
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

    def get(self, request):
        return render(
            request=request,
            template_name="dashboard/add-bank-details.html",
            context={"form": BankForm()},
        )
