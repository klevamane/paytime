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
    path("transactions/deposits", views.DepositView.as_view(), name="deposit_view_url"),
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
        views.MessageInboxDetail.as_view(),
        name="message_detail_view_url",
    ),
    path(
        "messages/inbox",
        views.MessageInboxList.as_view(),
        name="message_inbox_view_url",
    ),
    path(
        "messages/delete/<int:pk>",
        views.MessageDeleteView.as_view(),
        name="message_delete_view_url",
    ),
    path(
        "messages/sent",
        views.MessageSentListView.as_view(),
        name="message_sent_view_url",
    ),
    path(
        "messages/new",
        views.MessageCreateView.as_view(),
        name="message_new_view_url",
    ),
    # 🎒 💼 💼 💼 💼 ADMIN SECTION 💼 💼 💼 💼 🎒
    path(
        "admin",
        views.AdminDashboardIndexView.as_view(),
        name="admin_dashboard_view",
    ),
    # ADMIN PAYMENT REQUESTS
    path(
        "admin/payment-requests",
        views.AdminPaymentRequestsView.as_view(),
        name="admin_payment_requests_view",
    ),
    # ADMIN ALL USERS
    path(
        "admin/users",
        views.AdminAllUsersView.as_view(),
        name="admin_all_users_view",
    ),
    # ADMIN ALL Packages
    path(
        "admin/packages",
        views.AdminPackageView.as_view(),
        name="admin_packages_view",
    ),
    path(
        "admin/packages/update/<int:pk>",
        views.AdminPackageUpdateView.as_view(),
        name="admin_package_update_view",
    ),
    # ADMIN DOCUMENTS
    path(
        "admin/documents",
        views.AdminDocumentsView.as_view(),
        name="admin_documents_all_view",
    ),
    path(
        "admin/documents/update-user-document-status",
        views.update_user_document_status,
        name="update_user_document_status",
    ),
    # ADMIN SINGLE USER PROFILE
    path(
        "admin/users/profile/<int:pk>",
        views.AdminSingleUserProfileView.as_view(),
        name="admin_single_user_profile",
    ),
    # ADMIN MESSAGES
    path(
        "admin/messages",
        views.AdminMessageView.as_view(),
        name="admin_message_inbox_view",
    ),
    path(
        "admin/messages/<int:pk>",
        views.AdminMessageInboxDetail.as_view(),
        name="admin_inbox_detail_view",
    ),
    path(
        "admin/messages/sent",
        views.AdminMessagesSentView.as_view(),
        name="admin_messages_sent_view",
    ),
    path(
        "admin/messages/sent/<int:pk>",
        views.AdminMessageSentView.as_view(),
        name="admin_message_sent_view",
    ),
    path(
        "admin/messages/create",
        views.AdminMessageCreateView.as_view(),
        name="admin_message_create_view",
    ),
    # 🎒🎒🎒🎒🎒🎒🎒🎒🎒🎒🎒 💼 💼 💼 💼 TRANSACTIONS 💼 💼 💼 💼 🎒🎒🎒🎒🎒🎒🎒🎒🎒🎒🎒🎒
    path(
        "admin/transactions/all",
        views.AdminTransactionsAllView.as_view(),
        name="admin_all_transactions_view",
    ),
    path(
        "admin/transactions/users/withdrawals",
        views.AdminUsersWithdrawalView.as_view(),
        name="admin_users_withdrawals_transactions_view",
    ),
    path(
        "admin/transactions/users/deposits",
        views.AdminUsersDepositView.as_view(),
        name="admin_users_deposit_transactions_view",
    ),
    path(
        "admin/transactions/process_payment",
        views.process_payment,
        name="process_payment",
    ),
]
