from __future__ import absolute_import

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


def users_list(request):
    return render(request, "dashboard/users-list.html")


@login_required
def dashboard_data(request):
    return render(request, "dashboard/users-list.html")
