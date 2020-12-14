from __future__ import absolute_import

from django.urls import path

from dashboard import views

urlpatterns = [
    path("", views.users_list, name="dashboard-home"),
    path("add-bank-account", views.BankDetailsView.as_view(), name="add-bank-account"),
    path(
        "update-bank-account",
        views.BankUpdateView.as_view(),
        name="update-bank-account",
    ),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("documents", views.DocumentView.as_view(), name="documents"),
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
]
