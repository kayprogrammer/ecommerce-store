from django.shortcuts import render, redirect
from django.views import View
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.general.forms import SubscribeForm, MessageForm
from apps.general.models import Subscriber, Message
from apps.shop.models import Product
import sweetify


class HomeView(View):
    def get(self, request):
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by(
            "-created_at"
        )[:8]
        context = {"products": products}
        return render(request, "general/home.html", context=context)

    def post(self, request):
        # Subscribe to newsletter
        form = SubscribeForm(request.POST)
        if form.is_valid():
            Subscriber.objects.get_or_create(email=form.cleaned_data["email"])
            sweetify.success(
                request,
                title="Success",
                text="You have subscribed successfully",
                button="OK",
                timer=3000,
            )
        return redirect(request.META.get("HTTP_REFERER"))


class ContactView(View):
    def get(self, request):
        form = MessageForm()
        return render(request, "general/contact.html", context={"form": form})

    def post(self, request):
        print("Haaa")
        # Subscribe to newsletter
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(**form.cleaned_data)
            sweetify.success(
                request,
                title="Success",
                text="Message sent successfully",
                button="OK",
                timer=3000,
            )
            return redirect("/contact/")
        return render(request, "general/contact.html", context={"form": form})
