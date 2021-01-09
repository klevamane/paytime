# Generated by Django 3.1.5 on 2021-01-09 13:39

from __future__ import absolute_import

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finance", "0015_package_level"),
    ]

    operations = [
        migrations.AlterField(
            model_name="investment",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("cancelled", "Cancelled"),
                    ("completed", "Completed"),
                    ("pending", "Pending"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="roischedule",
            name="action",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("cancelled", "Cancelled"),
                    ("completed", "Completed"),
                    ("pending", "Pending"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="roischedule",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("cancelled", "Cancelled"),
                    ("completed", "Completed"),
                    ("pending", "Pending"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
