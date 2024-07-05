# Generated by Django 4.0 on 2024-06-15 10:51

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_user_created_at"),
        ("shop", "0007_alter_product_sizes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="colours",
            field=models.ManyToManyField(
                blank=True, related_name="products", to="shop.Colour"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="image2",
            field=models.ImageField(blank=True, upload_to="product_images/"),
        ),
        migrations.AlterField(
            model_name="product",
            name="image3",
            field=models.ImageField(blank=True, upload_to="product_images/"),
        ),
        migrations.AlterField(
            model_name="product",
            name="sizes",
            field=models.ManyToManyField(
                blank=True, related_name="products", to="shop.Size"
            ),
        ),
        migrations.CreateModel(
            name="Wishlist",
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
                ("guest_id", models.CharField(max_length=200, null=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist",
                        to="shop.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlist",
                        to="accounts.user",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="wishlist",
            constraint=models.UniqueConstraint(
                fields=("user", "product"), name="unique_user_product_wishlist_item"
            ),
        ),
        migrations.AddConstraint(
            model_name="wishlist",
            constraint=models.UniqueConstraint(
                fields=("guest_id", "product"),
                name="unique_guest_id_product_wishlist_item",
            ),
        ),
    ]
