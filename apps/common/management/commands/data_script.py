from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
from django.db import transaction
from apps.accounts.models import User
from apps.common.management.commands.seed import PRODUCT_CATEGORIES
from apps.shop.models import CATEGORY_IMAGE_PREFIX, Category
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
                    image_path = os.path.join(test_category_images_directory, image_file_name)
                    with open(image_path, 'rb') as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(f"{CATEGORY_IMAGE_PREFIX}{image_file_name}", image_file)
                        category = Category(name=category_name, slug=slug, image=file_path)
                        categories_to_create.append(category)
            Category.objects.bulk_create(categories_to_create)

    def create_products(self):
        categories = Category.objects.all()
        if not categories_exists:
            images = os.listdir(test_category_images_directory)
            categories_to_create = []
            for category_name in PRODUCT_CATEGORIES:
                with transaction.atomic():
                    slug = slugify(category_name)
                    image_file_name = self.get_image(images, slug)
                    image_path = os.path.join(test_category_images_directory, image_file_name)
                    with open(image_path, 'rb') as image_file:
                        file_storage = MediaCloudinaryStorage()
                        file_path = file_storage.save(f"{CATEGORY_IMAGE_PREFIX}{image_file_name}", image_file)
                        category = Category(name=category_name, slug=slug, image=file_path)
                        categories_to_create.append(category)
            Category.objects.bulk_create(categories_to_create)