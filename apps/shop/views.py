from django.http import Http404
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Category, Product

from apps.shop.utils import colour_size_filter_products, generic_products_ctx

PRODUCTS_PER_PAGE = 2

class ProductsView(ListView):
    model = Product
    paginate_by = PRODUCTS_PER_PAGE
    template_name = "shop/products.html"
    context_object_name = "products"

    def get_queryset(self):
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by(
            "-created_at"
        )
        return colour_size_filter_products(
            products,
            self.request.GET.getlist("size"),
            self.request.GET.getlist("color"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = context | generic_products_ctx()
        if self.request.htmx:
            self.template_name = "shop/product_list.html"
        return context


class ProductView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category").annotate(
            **REVIEWS_AND_RATING_ANNOTATION
        )
        product = products.prefetch_related("sizes", "colours", "reviews").get_or_none(
            slug=kwargs["slug"]
        )
        if not product:
            raise Http404("Product does not exist!")
        related_products = products.filter(category_id=product.category_id).exclude(
            id=product.id
        )[:10]
        context = {"product": product, "related_products": related_products}
        return render(request, "shop/product.html", context=context)


class ProductsByCategoryView(ListView):
    model = Product
    paginate_by = PRODUCTS_PER_PAGE
    template_name = "shop/products.html"
    context_object_name = "products"

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs["slug"])
        products = (
            Product.objects.filter(category=category)
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
            .order_by("-created_at")
        )
        return colour_size_filter_products(
            products,
            self.request.GET.getlist("size"),
            self.request.GET.getlist("color"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = context | generic_products_ctx()
        if self.request.htmx:
            self.template_name = "shop/product_list.html"
        return context
