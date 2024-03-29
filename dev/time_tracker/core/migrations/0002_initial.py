# Generated by Django 5.0.1 on 2024-01-08 04:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("employer", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeprofile",
            name="employer",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="employer.employer"
            ),
        ),
        migrations.AddField(
            model_name="employeeprofile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="timeentry",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
