from django.db import models
from autoslug import AutoSlugField
from apps.common.models import BaseModel

class Size(BaseModel):
    value = models.CharField(max_length=5)

class Colour(BaseModel):
    value = models.CharField(max_length=20)

class Category(BaseModel):
    name = models.CharField(max_length=20)
    slug = AutoSlugField(populate_from=name, always_update=True)

class Product(BaseModel):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from=name, always_update=True)
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=True)
    sizes = models.ManyToManyField(Size)
    colours = models.ManyToManyField(Colour)

class ProductImage():
    product = models.ForeignKey(Product, on_delete=models.C)