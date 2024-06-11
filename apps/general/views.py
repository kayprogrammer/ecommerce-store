from django.shortcuts import render
from django.views import View
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Product

class HomeView(View):
    def get(self, request):
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")[:8]
        context = {"products": products}
        return render(request, "general/home.html", context=context)
