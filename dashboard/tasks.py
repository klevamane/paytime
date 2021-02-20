from __future__ import absolute_import

from time import sleep

from celery import shared_task


@shared_task
def sleepy():
    sleep(15)
    print("*** DASHBOARD THINGS")
    return None
