from django.http import Http404, JsonResponse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from apps.shop.models import Category, Order, OrderItem, Product, Wishlist

from apps.shop.utils import colour_size_filter_products, generic_products_ctx, get_user_or_guest_id

PRODUCTS_PER_PAGE = 3

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


class WishlistView(ListView):
    def get(self, request):
        user, guest_id = get_user_or_guest_id(self.request)
        products = Product.objects.filter(wishlist__user=user, wishlist__guest_id=guest_id).annotate(**REVIEWS_AND_RATING_ANNOTATION).order_by("-created_at")                                        
        template = "shop/products.html"
        if request.htmx:
            template = "shop/product_list.html"
        products = colour_size_filter_products(
            products,
            request.GET.getlist("size"),
            request.GET.getlist("color"),
        )
        context = {"is_wishlist_page": True, "products": products} | generic_products_ctx()
        return render(request, template, context)

class ToggleWishlist(View):
    def get(self, request, *args, **kwargs):
        # Add or remove product from wishlist
        product = get_object_or_404(Product, slug=kwargs["slug"])
        user, guest_id = get_user_or_guest_id(request)
        wishlist, created = None, None
        wishlist, created = Wishlist.objects.get_or_create(user=user, guest_id=guest_id, product=product)
        if not created:
            wishlist.delete()
        response_data = {"created": created}
        if 'wishlist-page' in request.GET:
            response_data['remove'] = True
        return JsonResponse(response_data)

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

class CartView(View):
    def get(self, request):
        user, guest_id = get_user_or_guest_id(request)
        orderitems = OrderItem.objects.filter(user=user, guest_id=guest_id, order=None).select_related("product")
        context={"orderitems": orderitems}
        return render(request, "shop/cart.html", context=context)

class ToggleCartView(View):
    def get(self, request, *args, **kwargs):
        user, guest_id = get_user_or_guest_id(request)
        quantity = int(request.GET.get("quantity", 1))
        # If quantity is 0, then we delete item from cart
        product = get_object_or_404(Product, slug=kwargs["slug"])
        orderitem, created = OrderItem.objects.get_or_create(user=user, guest_id=guest_id, order=None, product=product)
        response_data = {"created": True}
        if not created:
            if quantity < 1:
                orderitem.delete()  
                response_data['created'] = False
            else:
                orderitem.quantity = quantity
                orderitem.save()
        return JsonResponse(response_data)
    
class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        # user = request.user
        # order = Order.objects.get(user=user, tx_ref=kwargs["tx_ref"])
        context={"order": "order"}
        return render(request, "shop/checkout.html", context=context)
    