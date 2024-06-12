from django.shortcuts import render, redirect
from django.views import View
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.general.forms import SubscribeForm
from apps.general.models import Subscriber
from apps.shop.models import Product
import sweetify

class HomeView(View):
    def get(self, request):
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")[:8]
        context = {"products": products}
        return render(request, "general/home.html", context=context)

    def post(self, request):
        # Subscribe to newsletter
        form = SubscribeForm(request.POST)
        if form.is_valid():
            Subscriber.objects.get_or_create(email=form.cleaned_data["email"])
            sweetify.success(request, title = "Success", text = "You have subscribed successfully", button="OK", timer=3000)
        return redirect(request.META.get("HTTP_REFERER"))
        