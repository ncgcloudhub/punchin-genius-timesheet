# Generated by Django 5.0.1 on 2024-01-14 05:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("employer", "0004_employerprofile_employer_alter_employer_employer_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="employer",
            options={
                "permissions": [
                    ("manage_employer_profile", "Can manage employer profile"),
                    ("view_employer_dashboard", "Can view employer dashboard"),
                    ("manage_employees", "Can add, edit, or remove employees"),
                    ("send_invitations", "Can send invitations to employees"),
                    ("view_employee_time_entries", "Can view employee time entries"),
                    ("edit_time_entries", "Can approve or edit time entries"),
                    ("generate_reports", "Can generate reports"),
                    ("manage_billing", "Can manage billing and subscriptions"),
                    ("set_alerts_reminders", "Can set up alerts and reminders"),
                    ("access_advanced_features", "Can access advanced features"),
                ]
            },
        ),
    ]
