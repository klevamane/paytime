from __future__ import absolute_import

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = "authentication"

    def ready(self):
        # trigger signal registration when this app is initialized
        import authentication.signals
