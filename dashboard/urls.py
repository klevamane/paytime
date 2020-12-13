from __future__ import absolute_import

from django.urls import path

from dashboard import views

urlpatterns = [
    path("", views.users_list, name="dashboard-home"),
    path("add-bank-account", views.BankDetailsView.as_view(), name="add-bank-account"),
    path("users", views.users_list, name="users-list"),
]
