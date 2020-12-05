from __future__ import absolute_import

from django.urls import path

from dashboard import views

urlpatterns = [
    path("", views.users_list, name="users-list"),
    path("users", views.users_list, name="users-list"),
]
