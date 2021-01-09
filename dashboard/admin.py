from __future__ import absolute_import

from django.contrib import admin

from dashboard.models import MessageCenter


@admin.register(MessageCenter)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "to", "message", "read", "created_at")
    list_display_links = ("id", "subject", "to", "message", "read")
    ordering = ("created_at",)
    search_fields = ("to", "read")
