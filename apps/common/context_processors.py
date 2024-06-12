from django.conf import settings
from django.db.models import Count
from apps.general.forms import SubscribeForm
from apps.general.models import SiteDetail
from apps.shop.models import Category


def sitedetail(request):
    sitedetail, _ = SiteDetail.objects.get_or_create()
    sitedetail.google_client_id = settings.GOOGLE_CLIENT_ID
    sitedetail.facebook_app_id = settings.FACEBOOK_APP_ID
    return {
        "sitedetail": sitedetail, 
        "categories": Category.objects.annotate(products_count=Count("products")).all(),
        "subscribe_form": SubscribeForm()
    }
