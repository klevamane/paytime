from __future__ import absolute_import

from django.contrib import admin

# Register your models here.
from finance.models import Investment, Package, RoiSchedule, Transactions


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "package", "status", "user", "created_at")
    list_display_links = ("id", "status", "user")
    ordering = ("status", "created_at")
    search_fields = ("status", "amount")


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "minimum_amount",
        "maximum_amount",
        "codename",
        "days",
        "return_on_investmentent",
        "level",
    )
    list_display_links = ("id", "codename")
    ordering = ("id", "name")


@admin.register(RoiSchedule)
class RoiScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "maturity_date", "investment", "action", "roi_amount")
    list_display_links = ("id", "action", "investment")
    ordering = ("action", "maturity_date", "created_at")
    search_fields = ("action", "maturity_date")


@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction_type",
        "amount",
        "status",
        "for_package",
        "user",
        "created_at",
    )
    list_display_links = ("id", "transaction_type", "status", "user")
    ordering = ("status", "created_at")
    search_fields = ("status",)
