from django.views import View
from django.shortcuts import render
from django.db.models import Count
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Colour, Product, Size

class ShopView(View):
    def get(self, request):
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")
        colors = Colour.objects.annotate(products_count=Count("products"))
        sizes = Size.objects.annotate(products_count=Count("products"))

        context = {"products": products, "colors": colors, "sizes": sizes}
        return render(request, "shop/shop.html", context=context)