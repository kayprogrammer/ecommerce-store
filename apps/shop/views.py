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
    queryset = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")
    paginate_by = PRODUCTS_PER_PAGE
    template_name = "shop/products.html"
    context_object_name = "products"

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
        return context
    
    def post(self, request):
        # Filter products by colour and sizes
        sizes = request.POST.getlist("size")
        colours = request.POST.getlist("color")
        products_original = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")

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
        products = products.distinct()

        # Pagination config
        paginated = Paginator(products, PRODUCTS_PER_PAGE)
        page_number = request.GET.get('page')
        page = paginated.get_page(page_number)
        is_paginated = True if page.paginator.num_pages > 1 else False

        context = {"page_obj": page, "is_paginated": is_paginated} | self.generic_ctx()
        print("Some stuffs: ", sizes, colours)
        return render(request, "shop/products.html", context=context)