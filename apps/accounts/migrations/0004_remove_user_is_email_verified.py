# Generated by Django 4.0 on 2024-05-21 19:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_avatar"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_email_verified",
        ),
    ]