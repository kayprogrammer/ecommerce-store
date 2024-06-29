from django.conf import settings
from django.db.models import Count
from apps.general.forms import SubscribeForm
from apps.general.models import SiteDetail
from apps.shop.models import Category, OrderItem
from apps.shop.utils import get_user_or_guest_id
from apps.shop.models import Wishlist

def sitedetail(request):
    sitedetail, _ = SiteDetail.objects.get_or_create()
    sitedetail.google_client_id = settings.GOOGLE_CLIENT_ID
    sitedetail.facebook_app_id = settings.FACEBOOK_APP_ID
    user, guest_id = get_user_or_guest_id(request)
    wishlist_count = Wishlist.objects.filter(user=user, guest_id=guest_id).count()
    orderitem_count = OrderItem.objects.filter(user=user, guest_id=guest_id).count()

    return {
        "sitedetail": sitedetail,
        "categories": Category.objects.annotate(products_count=Count("products")).all(),
        "subscribe_form": SubscribeForm(),
        "wishlist_count": wishlist_count,
        "orderitem_count": orderitem_count
    }
