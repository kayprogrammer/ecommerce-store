from django.views import View
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Count
from django.core.paginator import Paginator
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Colour, Product, Size
from typing import List

PRODUCTS_PER_PAGE = 2

class ShopView(ListView):
    model = Product
    paginate_by = PRODUCTS_PER_PAGE
    template_name = "shop/products.html"
    context_object_name = "products"

    def get_queryset(self):
        products_original = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")
        products = products_original
        sized_products = None
        coloured_products = None
        sizes = self.request.GET.getlist("size")
        colours = self.request.GET.getlist("color")

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
        

    def generic_ctx(self):
        products = Product.objects.all()
        context = {}
        context["colors"] = Colour.objects.annotate(products_count=Count("products"))
        context["sizes"] = Size.objects.annotate(products_count=Count("products"))
        context["color_products_count"] = products.exclude(colours=None).count()
        context["sized_products_count"] = products.exclude(sizes=None).count()
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = context | self.generic_ctx() 
        if self.request.htmx:
            self.template_name = 'shop/product_list.html'
        return context
