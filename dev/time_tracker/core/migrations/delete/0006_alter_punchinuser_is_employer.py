# Generated by Django 5.0 on 2024-01-06 03:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_alter_punchinuser_first_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="punchinuser",
            name="is_employer",
            field=models.BooleanField(default=False, verbose_name="Employer Status"),
        ),
    ]
