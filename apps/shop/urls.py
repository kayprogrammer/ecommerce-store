from django.urls import path
from . import views

urlpatterns = [
    path("shop/", views.ProductsView.as_view(), name="products"),
    path("shop/products/<slug:slug>/", views.ProductView.as_view(), name="product"),
    path(
        "shop/categories/<slug:slug>/",
        views.ProductsByCategoryView.as_view(),
        name="category_products",
    ),
    path("shop/wishlist", views.WishlistView.as_view(), name="wishlist"),
]
