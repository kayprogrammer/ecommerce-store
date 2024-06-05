from django.shortcuts import render
from django.views import View
from django.db.models import Count
from apps.shop.models import Category

class HomeView(View):
    def get(self, request):
        categories = Category.objects.annotate(products_count=Count("products")).all()
        context = {"categories": categories}
        return render(request, "general/home.html", context=context)