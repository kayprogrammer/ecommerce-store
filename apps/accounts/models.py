from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from .managers import CustomUserManager


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    first_name = models.CharField(
        verbose_name=(_("First name")), max_length=25, null=True
    )
    last_name = models.CharField(
        verbose_name=(_("Last name")), max_length=25, null=True
    )
    email = models.EmailField(verbose_name=(_("Email address")), unique=True)
    avatar = models.URLField(default=settings.DEFAULT_AVATAR_URL)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name
