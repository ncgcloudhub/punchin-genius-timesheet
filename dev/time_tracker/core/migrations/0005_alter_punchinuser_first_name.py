# Generated by Django 5.0 on 2023-12-29 05:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_punchinuser_first_name_punchinuser_last_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="punchinuser",
            name="first_name",
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
    ]
