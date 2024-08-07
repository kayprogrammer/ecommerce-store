# Generated by Django 4.0 on 2024-07-04 23:56

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0011_order_coupon_alter_order_shipping_address"),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200, unique=True)),
                ("code", models.CharField(max_length=20, unique=True)),
                ("phone_code", models.CharField(max_length=20, unique=True)),
            ],
            options={
                "verbose_name_plural": "Countries",
            },
        ),
    ]
