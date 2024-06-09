from django.shortcuts import render
from django.views import View
from django.db.models import Count
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Category, Product

class HomeView(View):
    def get(self, request):
        categories = Category.objects.annotate(products_count=Count("products")).all()
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")[:8]
        context = {"categories": categories, "products": products}
        return render(request, "general/home.html", context=context)
