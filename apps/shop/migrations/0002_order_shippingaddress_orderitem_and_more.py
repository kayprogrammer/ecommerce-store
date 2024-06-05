# Generated by Django 4.0 on 2024-05-14 12:53

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_avatar"),
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tx_ref", models.CharField(blank=True, max_length=100, unique=True)),
                (
                    "date_ordered",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "delivery_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("PACKING", "PACKING"),
                            ("SHIPPING", "SHIPPING"),
                            ("ARRIVING", "ARRIVING"),
                            ("SUCCESS", "SUCCESS"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("SUCCESSFUL", "SUCCESSFUL"),
                            ("CANCELLED", "CANCELLED"),
                            ("FAILED", "FAILED"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("date_delivered", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShippingAddress",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=1000)),
                ("email", models.EmailField(max_length=1000)),
                ("phone", models.CharField(max_length=20, null=True)),
                ("address", models.CharField(max_length=1000, null=True)),
                ("city", models.CharField(max_length=200, null=True)),
                ("state", models.CharField(max_length=200, null=True)),
                ("country", models.CharField(max_length=200, null=True)),
                ("zipcode", models.IntegerField(null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping_addresses",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("guest_id", models.CharField(max_length=100, null=True)),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "color",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shop.colour",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orderitems",
                        to="shop.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="shop.product"
                    ),
                ),
                (
                    "size",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shop.size",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.user",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_address",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="shop.shippingaddress",
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="accounts.user",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                fields=("user", "product", "order"),
                name="unique_user_product_orderitems",
            ),
        ),
        migrations.AddConstraint(
            model_name="orderitem",
            constraint=models.UniqueConstraint(
                fields=("guest_id", "product", "order"),
                name="unique_guest_id_product_orderitems",
            ),
        ),
    ]
