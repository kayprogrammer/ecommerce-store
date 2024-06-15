from django.urls import path
from . import views

urlpatterns = [
    path("shop/", views.ProductsView.as_view(), name="products"),
    path("shop/<slug:slug>/", views.ProductView.as_view(), name="product"),
    path(
        "shop/categories/<slug:slug>/",
        views.ProductsByCategoryView.as_view(),
        name="category_products",
    ),
]
