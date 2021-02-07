# -*- coding: utf-8 -*-
from __future__ import absolute_import

import requests
from django.db import migrations


def add_new_bank(apps, schema_editor):

    Banks = apps.get_model("finance", "Banks")
    response = requests.get("https://api.paystack.co/bank")
    if response.status_code == 200:
        banks = response.json().get("data")
        for bank in banks:
            name = bank.get("name")
            slug = bank.get("slug")
            code = bank.get("code")
            country = bank.get("country")
            bank = Banks(code=code, country=country, slug=slug, name=name)
            bank.save()


def remove_banks(apps, schema_editor):
    """Remove new Banks"""
    Banks = apps.get_model("finance", "Banks")
    Banks.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [("finance", "0023_auto_20210207_1013")]
    operations = [migrations.RunPython(add_new_bank, remove_banks)]
