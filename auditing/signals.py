from __future__ import absolute_import

from django.db.models.signals import post_save
from django.dispatch import receiver

from auditing.models import CREATE, ModelChange
from finance.models import Bank, Investment, Transactions
from user.models import User


# Remember to add the signals to the app/apps.py file
# and __init__.py
@receiver(post_save, sender=Investment)
@receiver(post_save, sender=Transactions)
@receiver(post_save, sender=User)
@receiver(post_save, sender=Bank)
def create_object(sender, instance, created, **kwargs):
    if created:
        changes = get_changes(instance)
        user = instance if isinstance(instance, User) else instance.user
        ModelChange(user=user, kind=CREATE, primary=instance, changes=changes).save()


def get_changes(instance):
    message = None
    if isinstance(instance, Bank):
        message = "{} has added a new bank account detail".format(
            instance.user.get_short_name()
        )
    if isinstance(instance, User):
        message = "New user with email: {}".format(instance.email)
    elif isinstance(instance, Investment):
        message = "New investment of {} of {} package".format(
            instance.amount, instance.package.name
        )
    elif isinstance(instance, Transactions):
        if instance.transaction_type == "withdrawal":
            message = "New withdrawl request of {}".format(instance.amount)

    return {"message": message} if message else {}
