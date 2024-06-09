from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
from django.db import transaction
from apps.accounts.models import User
from apps.common.management.commands.seed import (
    PRODUCT_CATEGORIES,
    PRODUCT_DATA,
    SIZES_DATA,
    COLOUR_DATA,
)
from apps.shop.models import (
    CATEGORY_IMAGE_PREFIX,
    PRODUCT_IMAGE_PREFIX,
    Category,
    Product,
    Size,
    Colour,
)
from cloudinary_storage.storage import MediaCloudinaryStorage
import os

CURRENT_DIR = Path(__file__).resolve().parent
test_images_directory = os.path.join(CURRENT_DIR, "images")
test_category_images_directory = f"{test_images_directory}/categories"
test_product_images_directory = f"{test_images_directory}/products"


class CreateData(object):
    def __init__(self) -> None:
        self.create_superuser()
        self.create_reviewer()
        self.create_categories()
        sizes, colours = self.create_sizes_and_colours()
        self.create_products(sizes, colours)

    def create_superuser(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_superuser": True,
            "is_staff": True,
        }
        superuser = User.objects.get_or_none(email=user_dict["email"])
        if not superuser:
            superuser = User.objects.create_user(**user_dict)
        return superuser

    def create_reviewer(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Reviewer",
            "email": settings.FIRST_REVIEWER_EMAIL,
            "password": settings.FIRST_REVIEWER_PASSWORD,
        }
        reviewer = User.objects.get_or_none(email=user_dict["email"])
        if not reviewer:
            reviewer = User.objects.create_user(**user_dict)
        return reviewer

    def get_image(self, images_list, substring):
        return next((s for s in images_list if s.startswith(substring)), None)

    def create_categories(self):
        categories_exists = Category.objects.exists()
        if not categories_exists:
            images = os.listdir(test_category_images_directory)
            categories_to_create = []
            for category_name in PRODUCT_CATEGORIES:
                with transaction.atomic():
                    slug = slugify(category_name)
                    image_file_name = self.get_image(images, slug)
                    image_path = os.path.join(
                        test_category_images_directory, image_file_name
                    )
                    with open(image_path, "rb") as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(
                            f"{CATEGORY_IMAGE_PREFIX}{image_file_name}", image_file
                        )
                        category = Category(
                            name=category_name, slug=slug, image=file_path
                        )
                        categories_to_create.append(category)
            Category.objects.bulk_create(categories_to_create)

    def create_sizes_and_colours(self):
        sizes = Size.objects.all()
        colours = Colour.objects.all()
        if not sizes.exists():
            sizes_to_create = [Size(value=size) for size in SIZES_DATA]
            Size.objects.bulk_create(sizes_to_create)
        if not colours.exists():
            colours_to_create = [Colour(value=colour) for colour in COLOUR_DATA]
            Colour.objects.bulk_create(colours_to_create)
        return sizes, colours

    def create_products(self, sizes, colours):
        products_exists = Product.objects.exists()
        if not products_exists:
            with transaction.atomic():
                images = os.listdir(test_product_images_directory)
                products_to_create = []
                file_paths_created = []
                for idx, product_data in enumerate(PRODUCT_DATA):
                    category_slug = product_data["category_slug"]
                    category = Category.objects.get_or_none(slug=category_slug)
                    if not category:
                        pass
                    image_file_name = self.get_image(images, category_slug)
                    image_path = os.path.join(
                        test_product_images_directory, image_file_name
                    )
                    with open(image_path, "rb") as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(
                            f"{PRODUCT_IMAGE_PREFIX}{image_file_name}", image_file
                        )
                        product = Product(
                            name=product_data["name"],
                            category=category,
                            desc="This is a good product you'll never regret. It is of good quality",
                            price_old=(idx + 1) * 5000,
                            price_current=(idx + 1) * 4000,
                            image1=file_path
                        )
                        products_to_create.append(product)
                products_created = Product.objects.bulk_create(products_to_create)

                # Product update sizes and colours
                for product in products_created:
                    product.sizes.set(sizes)
                    product.colours.set(colours)
        pass
