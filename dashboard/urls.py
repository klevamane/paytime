from __future__ import absolute_import

from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from dashboard import views
from paytime import settings

urlpatterns = [
    path("", views.users_list, name="dashboard-home"),
    # profile
    path("profile", views.ProfileView.as_view(), name="profile_url"),
    path(
        "profile-details-submit",
        views.HandleProfileSubmit.as_view(),
        name="profile-details-submit-url",
    ),
    path(
        "bank-details-submit",
        views.HandleBankSubmit.as_view(),
        name="bank-details-submit-url",
    ),
    path("profile/documents", views.DocumentView.as_view(), name="documents"),
    path("users", views.users_list, name="users-list"),
    # Transactions
    path("transactions/deposit", views.DepositView.as_view(), name="deposit_view_url"),
    path(
        "transactions/withrawal",
        views.WithdrawalView.as_view(),
        name="withdrawal_view_url",
    ),
    path(
        "transactions/all",
        views.TransactionsAllView.as_view(),
        name="transactions_all_url",
    ),
    # Wallet
    path(
        "wallet",
        views.WalletView.as_view(),
        name="wallet_url",
    ),
    path(
        "investments/invest",
        views.InvestView.as_view(),
        name="invest_view_url",
    ),
    path(
        "investments/payment",
        views.PaymentView.as_view(),
        name="payment_view_url",
    ),
    path(
        "investments",
        views.InvestmentsView.as_view(),
        name="investments_view_url",
    ),
    path(
        "investments/detail/<int:id>",
        views.InvestmentDetailView.as_view(),
        name="investment_detail_view_url",
    ),
    path(
        "investments/payment/verification",
        csrf_exempt(views.PaymentVerificationView.as_view()),
        name="verify_payment_url",
    ),
    path(
        "investments/payment/validate-payment-package-amount",
        csrf_exempt(views.validate_package_amount),
        name="payment_package_amount_url",
    ),
    path(
        "investments/payment/get-package-details/<str:codename>",
        csrf_exempt(views.PackageDetail.as_view()),
        name="package_detail_view_url",
    ),
    path(
        "investments/detail/transfer-to-wallet/<int:roi_id>",
        csrf_exempt(views.TransferToWalletView.as_view()),
        name="transfer-to-wallet_url",
    ),
    # Messages
    path(
        "messages/inbox/detail/<int:pk>",
        views.MessageDetail.as_view(),
        name="message_inbox_detail_view_url",
    ),
    path(
        "messages/inbox",
        views.MessageInboxList.as_view(),
        name="message_inbox_view_url",
    ),
    path(
        "messages/new",
        views.MessageCreateView.as_view(),
        name="message_new_view_url",
    ),
]
