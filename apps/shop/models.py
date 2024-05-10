from django.db import models
from autoslug import AutoSlugField
from apps.accounts.models import User
from apps.common.models import BaseModel

class Size(BaseModel):
    value = models.CharField(max_length=5)

    def __str__(self):
        return str(self.value)
    
class Colour(BaseModel):
    value = models.CharField(max_length=20)

    def __str__(self):
        return str(self.value)
    
class Category(BaseModel):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from=name, always_update=True)

    def __str__(self):
        return str(self.name)
    
class Product(Category):
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    sizes = models.ManyToManyField(Size)
    colours = models.ManyToManyField(Colour)

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return str(self.product.name)
    
RATING_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5)
)

class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=RATING_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.user.full_name}----{self.product.name}"
    
