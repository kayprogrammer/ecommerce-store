# Generated by Django 4.0 on 2024-07-16 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0021_order_payment_gateway"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="payment_gateway",
            new_name="payment_method",
        ),
    ]
