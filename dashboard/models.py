from __future__ import absolute_import

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models

# Create your models here.
from user.models import User


class TimeStampMixin(models.Model):
    class Meta:
        # making abstract will also prevent this model from
        # creating a table (only inheritable)
        abstract = True

    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


class MessageCenter(LoginRequiredMixin, TimeStampMixin):
    subject = models.CharField(max_length=30)
    message = models.CharField(max_length=30)
    # if to is None, then the message is directed to the admin(s)
    to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
