from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "partials/base-dashboard.html")


def signup(request):
    return render(request, "authentication/signup.html")


def login(request):
    return render(request, "authentication/login.html")
