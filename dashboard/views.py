from __future__ import absolute_import

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views import View

from finance.forms import BankForm
from finance.models import Bank
from paytime.utils import FAILURE_MESSAGES, SUCCESS_MESSAGES


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


class ProfileView(View):
    def get(self, request):
        return render(request=request, template_name="dashboard/profile/profile.html")


class DocumentView(View):
    def get(self, request):
        return render(request=request, template_name="dashboard/profile/documents.html")
