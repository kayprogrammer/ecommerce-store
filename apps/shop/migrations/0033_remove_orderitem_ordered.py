# Generated by Django 5.0 on 2024-07-25 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "shop",
            "0032_remove_orderitem_unique_guest_id_product_order_orderitems_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderitem",
            name="ordered",
        ),
    ]