from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductsView.as_view(), name="products"),
    path("products/<slug:slug>/", views.ProductView.as_view(), name="product"),
    path(
        "categories/<slug:slug>/",
        views.ProductsByCategoryView.as_view(),
        name="category_products",
    ),
    path("wishlist", views.WishlistView.as_view(), name="wishlist"),
    path("toggle-wishlist/<slug:slug>/", views.ToggleWishlist.as_view(), name="toggle-wishlist"),
    path("cart/", views.CartView.as_view(), name="cart"),
]
