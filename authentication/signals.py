from __future__ import absolute_import

from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def user_signed_up_(request, user, sociallogin=None, **kwargs):
    """
    Update the recently signed up user with details from
    the social profile
    the reason being that normally when a user signs up using
    google, the firstname and lastname isn't automatically updated
    therefore we need to maually account for this

    Args:
        request: The request
        user: The recently created user
        soliallogin: This value is set to True if signup was done via social auth
    """
    if sociallogin and sociallogin.account.provider == "google":
        user.firstname = sociallogin.account.extra_data["given_name"]
        user.lastname = sociallogin.account.extra_data["family_name"]
        user.save()
