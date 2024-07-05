import secrets
import uuid
from django.db import models
from django.utils import timezone
from .managers import GetOrNoneManager


class BaseModel(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True

    @property
    def image_url(self):
        url = None
        if hasattr(self, "image"):
            try:
                url = self.image.url
            except:
                url = None
        return url


def generate_unique_code(model: BaseModel, field):
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    unique_code = "".join(secrets.choice(allowed_chars) for i in range(12))
    code = unique_code
    similar_coupon = model.objects.filter(**{field: code}).exists()
    if not similar_coupon:
        return code
    generate_unique_code()


def image_folder_to_upload(subfolder=""):
    folder = f"ecommerce-store/{subfolder}/"
    if subfolder == "":
        folder = "ecommerce-store/"
    return folder
