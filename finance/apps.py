from __future__ import absolute_import

from django.apps import AppConfig


class FinanceConfig(AppConfig):
    name = "finance"

    def ready(self):
        # trigger signal registration when this app is initialized
        import finance.signals
