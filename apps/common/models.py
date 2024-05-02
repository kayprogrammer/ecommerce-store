import uuid
from django.db import models
from .managers import GetOrNoneManager


class BaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True


def image_folder_to_upload(subfolder=""):
    folder = f"ecommerce-store/{subfolder}/"
    if subfolder == "":
        folder = "ecommerce-store/"
    return folder
