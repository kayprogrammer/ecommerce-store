from apps.shop.models import Colour, Product, Size
from django.db.models import Count


def generic_products_ctx():
    products = Product.objects.all()
    context = {}
    context["colors"] = Colour.objects.annotate(products_count=Count("products"))
    context["sizes"] = Size.objects.annotate(products_count=Count("products"))
    context["color_products_count"] = products.exclude(colours=None).count()
    context["sized_products_count"] = products.exclude(sizes=None).count()
    return context


def colour_size_filter_products(products_original, sizes, colours):
    products = products_original
    sized_products = None
    coloured_products = None

    if len(sizes) > 0:
        sized_products = products_original.exclude(sizes=None)
        if not "ALL" in sizes:
            sized_products = products_original.filter(sizes__value__in=sizes)
        products = sized_products

    if len(colours) > 0:
        coloured_products = products_original.exclude(colours=None)
        if not "ALL" in colours:
            coloured_products = products_original.filter(colours__value__in=colours)
        products = coloured_products

    if sized_products and coloured_products:
        products = sized_products | coloured_products
    return products.distinct()


def get_user_or_guest_id(request):
    user = request.user
    if user.is_authenticated:
        return user, None
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
    return None, request.session.session_key
