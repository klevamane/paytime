from __future__ import absolute_import

from django.apps import AppConfig


class AuditingConfig(AppConfig):
    name = "auditing"

    def ready(self):
        # trigger signal registration when this app is initialized
        import auditing.signals
