from __future__ import absolute_import
from django.shortcuts import render

# Create your views here.


def users_list(request):
    return render(request, "dashboard/users-list.html")
