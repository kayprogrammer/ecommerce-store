# Generated by Django 5.0 on 2024-07-25 13:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0025_alter_orderitem_guest_id_alter_orderitem_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="orderitem",
            name="unique_user_product_orderitems",
        ),
        migrations.RemoveConstraint(
            model_name="orderitem",
            name="unique_guest_id_product_orderitems",
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                fields=(
                    "user",
                    "product",
                    "order_id",
                    "ordered",
                    "size_id",
                    "color_id",
                ),
                name="unique_user_product_orderitems",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                fields=(
                    "guest_id",
                    "product",
                    "order_id",
                    "ordered",
                    "size_id",
                    "color_id",
                ),
                name="unique_guest_id_product_orderitems",
            ),
        ),
    ]
