# Generated by Django 3.1.5 on 2021-02-07 00:45

from __future__ import absolute_import

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0006_auto_20210109_1339"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
