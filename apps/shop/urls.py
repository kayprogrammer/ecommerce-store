from django.urls import path
from . import views

urlpatterns = [
    path("shop/", views.ShopView.as_view(), name="shop")
]