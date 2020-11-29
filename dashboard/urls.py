from __future__ import absolute_import
from django.urls import path
from dashboard import views

urlpatterns = [
    path("users", views.users_list, name="users-list"),
]
