# Generated by Django 4.0 on 2024-07-16 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0020_remove_orderitem_unique_user_product_orderitems_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_gateway",
            field=models.CharField(
                choices=[("PAYSTACK", "PAYSTACK"), ("PAYPAL", "PAYPAL")],
                max_length=20,
                null=True,
            ),
        ),
    ]
