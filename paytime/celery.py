from __future__ import absolute_import

import os

from .celery import Celery

# This is for celery confifuration in our app
# but the tasks that celery will run, will come from our
# django app
# set the default Django settings module for the 'celery' program.

# it allows celery to look into our djano app and see
# what tasks has been defined/set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paytime.settings")

# This creates a new instance of celery
app = Celery("paytime")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# this loads the setting
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
# this will discover all the tasks that we have set up
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
