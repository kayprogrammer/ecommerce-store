from apps.shop.models import OrderItem, Wishlist
from apps.shop.utils import get_user_or_guest_id


def move_wishlist_and_cart_items_to_user(request, user):
    _, guest_id = get_user_or_guest_id(request)

    # For wishlist
    Wishlist.objects.filter(guest_id=guest_id).exclude(
        product_id__in=Wishlist.objects.filter(user=user).values_list(
            "product_id", flat=True
        )
    ).update(guest_id=None, user=user)

    # For cart
    user_order_items = OrderItem.objects.filter(user=user, order=None).values_list(
        "product_id", "size_id", "color_id", flat=False
    )
    # Convert to a set of tuples for easy checking
    user_order_items_set = set(user_order_items)
    # Retrieve guest's order items
    guest_order_items = OrderItem.objects.filter(guest_id=guest_id)

    # Prepare items to update
    items_to_update = []
    for item in guest_order_items:
        item_tuple = (item.product_id, item.size_id, item.color_id)
        if item_tuple not in user_order_items_set:
            item.guest_id = None
            item.user = user
            items_to_update.append(item)

    if len(items_to_update) > 0:
        OrderItem.objects.bulk_update(items_to_update, ["guest_id", "user"])
