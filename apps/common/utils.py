from django.db.models import Avg, Value, FloatField, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from apps.accounts.models import User
from apps.shop.models import Category, Colour, Country, Product, Size

REVIEWS_AND_RATING_ANNOTATION = {
    "reviews_count": Count("reviews"),
    "avg_rating": Coalesce(Avg("reviews__rating"), Value(0), output_field=FloatField()),
}


class TestUtil:
    def new_user():
        user_dict = {
            "first_name": "Test",
            "last_name": "Name",
            "email": "test@example.com",
            "password": "testpassword",
        }
        user = User.objects.create_user(**user_dict)
        return user

    def another_user():
        create_user_dict = {
            "first_name": "AnotherTest",
            "last_name": "User",
            "email": "anothertestuser@example.com",
            "password": "anothertestuser123",
        }
        user = User.objects.create_user(**create_user_dict)
        return user

    def create_category():
        category, _ = Category.objects.get_or_create(name="TestCategory")
        return category

    def create_size_and_color():
        size, _ = Size.objects.get_or_create(value="M")
        color, _ = Colour.objects.get_or_create(value="Black")
        return size, color

    def create_product():
        # Create Category
        category = TestUtil.create_category()
        size, color = TestUtil.create_size_and_color()
        # Create Product
        product_dict = {
            "name": "New Test Listing",
            "desc": "New description",
            "category": category,
            "price_old": 1000.00,
            "price_current": 500.00,
            "in_stock": 100,
        }
        product, _ = Product.objects.get_or_create(
            name=product_dict["name"], defaults=product_dict
        )
        product.sizes.add(size)
        product.colours.add(color)
        return product

    def create_country(self):
        country, _ = Country.objects.get_or_create(name="TestCountry", code="TC")
        return country
