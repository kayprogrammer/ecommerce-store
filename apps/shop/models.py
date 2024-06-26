from distutils.command import upload
import secrets
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from autoslug import AutoSlugField
from django.urls import reverse
from apps.accounts.models import User
from apps.common.models import BaseModel
from apps.shop.choices import (
    DELIVERY_STATUS_CHOICES,
    PAYMENT_STATUS_CHOICES,
    RATING_CHOICES,
)
from django.utils import timezone

CATEGORY_IMAGE_PREFIX = "category_images/"
PRODUCT_IMAGE_PREFIX = "product_images/"


class Size(BaseModel):
    value = models.CharField(max_length=5, unique=True)

    def __str__(self):
        return str(self.value)


class Colour(BaseModel):
    value = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return str(self.value)


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    image = models.ImageField(upload_to=CATEGORY_IMAGE_PREFIX)

    def __str__(self):
        return str(self.name)

    @property
    def get_absolute_url(self):
        return reverse("category_products", kwargs={"slug": self.slug})

    class Meta:
        verbose_name_plural = "Categories"


class Product(BaseModel):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", unique=True, always_update=True)
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    sizes = models.ManyToManyField(Size, related_name="products", blank=True)
    colours = models.ManyToManyField(Colour, related_name="products", blank=True)
    in_stock = models.IntegerField(default=5)

    # Only 3 images are allowed
    image1 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX)
    image2 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX, blank=True)
    image3 = models.ImageField(upload_to=PRODUCT_IMAGE_PREFIX, blank=True)

    def return_img_url(self, image: ImageFieldFile):
        try:
            url = image.url
        except:
            url = None
        return url

    @property
    def image1_url(self):
        return self.return_img_url(self.image1)

    @property
    def image2_url(self):
        return self.return_img_url(self.image2)

    @property
    def image3_url(self):
        return self.return_img_url(self.image3)

    @property
    def get_absolute_url(self):
        return reverse("product", kwargs={"slug": self.slug})

class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist")
    guest_id = models.CharField(max_length=200, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_wishlist_item",
            ),
            models.UniqueConstraint(
                fields=["guest_id", "product"],
                name="unique_guest_id_product_wishlist_item",
            ),
        ]

class ShippingAddress(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    full_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=1000)
    phone = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    zipcode = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.full_name}'s shipping details"


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    tx_ref = models.CharField(max_length=100, blank=True, unique=True)
    date_ordered = models.DateTimeField(default=timezone.now)
    delivery_status = models.CharField(
        max_length=20, default="PENDING", choices=DELIVERY_STATUS_CHOICES
    )
    payment_status = models.CharField(
        max_length=20, default="PENDING", choices=PAYMENT_STATUS_CHOICES
    )
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.CASCADE, blank=True, null=True
    )
    date_delivered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name}'s order"

    def save(self, *args, **kwargs) -> None:
        while not self.tx_ref:
            allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
            unique_code = "".join(secrets.choice(allowed_chars) for i in range(10))
            tx_ref = unique_code
            similar_obj_tx_ref = Order.objects.filter(tx_ref=tx_ref).exists()
            if not similar_obj_tx_ref:
                self.tx_ref = tx_ref
        super().save(*args, **kwargs)

    @property
    def get_cart_total(self):
        orderitems = self.orderitems.all()
        total = sum([item.get_total for item in orderitems])
        return total


class OrderItem(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    guest_id = models.CharField(max_length=100, null=True)
    order = models.ForeignKey(
        Order,
        related_name="orderitems",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    color = models.ForeignKey(Colour, on_delete=models.CASCADE, null=True)

    @property
    def get_total(self):
        return self.product.price_current * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product", "order"],
                name="unique_user_product_orderitems",
            ),
            models.UniqueConstraint(
                fields=["guest_id", "product", "order"],
                name="unique_guest_id_product_orderitems",
            ),
        ]

    def __str__(self):
        return str(self.product.name)


class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.user.full_name}----{self.product.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_reviews",
            ),
        ]
