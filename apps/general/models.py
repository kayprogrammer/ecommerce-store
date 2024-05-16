from turtle import mode
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class SiteDetail(BaseModel):
    name = models.CharField(max_length=300, default="E-Store")
    email = models.EmailField(default="kayprogrammer1@gmail.com")
    phone = models.CharField(max_length=300, default="+2348133831036")
    address = models.CharField(max_length=300, default="234, Lagos, Nigeria")
    fb = models.CharField(
        max_length=300, verbose_name=(_("Facebook")), default="https://facebook.com"
    )
    tw = models.CharField(
        max_length=300, verbose_name=(_("Twitter")), default="https://twitter.com"
    )
    wh = models.CharField(
        max_length=300,
        verbose_name=(_("Whatsapp")),
        default="https://wa.me/2348133831036",
    )
    ig = models.CharField(
        max_length=300, verbose_name=(_("Instagram")), default="https://instagram.com"
    )
    map_url = models.URLField(max_length=10000, default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3001156.4288297426!2d-78.01371936852176!3d42.72876761954724!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4ccc4bf0f123a5a9%3A0xddcfc6c1de189567!2sNew%20York%2C%20USA!5e0!3m2!1sen!2sbd!4v1603794290143!5m2!1sen!2sbd")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding and SiteDetail.objects.exists():
            raise ValidationError("There can be only one Site Detail instance")

        return super(SiteDetail, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Site details"


class Subscriber(BaseModel):
    email = models.EmailField()
    exported = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Message(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    text = models.TextField()
    addressed = models.BooleanField(default=False)

    def __str__(self):
        return self.name