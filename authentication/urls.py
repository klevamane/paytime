from __future__ import absolute_import

from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from authentication import views

urlpatterns = [
    path("", views.index, name="index"),
    path("forgot-password", views.forgot_password, name="forgotpwd"),
    path(
        "validate-user-email",
        # exempt this so that we wont keep
        # running into permission denied 403 status code
        # TODO: validate the is email
        csrf_exempt(views.validate_user_email_view),
        name="validate-user-email",
    ),
    path("accounts/profile/", views.not_found, name="404"),
    path(
        "activate/<uidb64>/<token>", views.VerificationView.as_view(), name="activate"
    ),
]
