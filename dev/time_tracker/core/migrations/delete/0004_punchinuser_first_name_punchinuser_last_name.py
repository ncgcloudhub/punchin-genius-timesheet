# Generated by Django 4.2.7 on 2023-12-26 05:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_punchinuser_is_employer"),
    ]

    operations = [
        migrations.AddField(
            model_name="punchinuser",
            name="first_name",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name="punchinuser",
            name="last_name",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
