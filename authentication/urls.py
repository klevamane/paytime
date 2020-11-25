from django.urls import path
from authentication import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup", views.signup, name="signup")
]
