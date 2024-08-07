# Generated by Django 5.0 on 2024-07-25 18:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0027_remove_orderitem_unique_user_product_orderitems_and_more"),
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
                condition=models.Q(("order__isnull", False)),
                fields=("user", "product", "order", "ordered", "size", "color"),
                name="unique_user_product_orderitems",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                condition=models.Q(("order__isnull", False)),
                fields=("guest_id", "product", "order", "ordered", "size", "color"),
                name="unique_guest_id_product_orderitems",
            ),
        ),
    ]
