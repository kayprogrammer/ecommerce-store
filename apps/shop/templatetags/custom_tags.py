from django import template

from apps.shop.models import Wishlist
from apps.shop.utils import get_user_or_guest_id

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context["request"].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

@register.filter
def wishlist_state(product_id, request):
    user, guest_id = get_user_or_guest_id(request)
    wishlist_exists = False
    if user:
        wishlist_exists = Wishlist.objects.filter(user=user, product_id=product_id).exists()
    else:
        wishlist_exists = Wishlist.objects.filter(guest_id=guest_id, product_id=product_id).exists()
    return "fas fa-heart" if wishlist_exists else "far fa-heart"

@register.filter
def sub(value, arg):
    return value - arg