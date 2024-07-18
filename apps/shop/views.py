from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.accounts.mixins import LoginRequiredMixin
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from .forms import ShippingAddressForm
from .models import (
    Category,
    Coupon,
    Order,
    OrderItem,
    Product,
    ShippingAddress,
    Wishlist,
)

from .utils import (
    colour_size_filter_products,
    generic_products_ctx,
    get_user_or_guest_id,
)
import sweetify

PRODUCTS_PER_PAGE = 15


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
        products = (
            Product.objects.filter(wishlist__user=user, wishlist__guest_id=guest_id)
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
            .order_by("-created_at")
        )
        template = "shop/products.html"
        if request.htmx:
            template = "shop/product_list.html"
        products = colour_size_filter_products(
            products,
            request.GET.getlist("size"),
            request.GET.getlist("color"),
        )
        context = {
            "is_wishlist_page": True,
            "products": products,
        } | generic_products_ctx()
        return render(request, template, context)


class ToggleWishlist(View):
    def get(self, request, *args, **kwargs):
        # Add or remove product from wishlist
        product = get_object_or_404(Product, slug=kwargs["slug"])
        user, guest_id = get_user_or_guest_id(request)
        wishlist, created = None, None
        wishlist, created = Wishlist.objects.get_or_create(
            user=user, guest_id=guest_id, product=product
        )
        if not created:
            wishlist.delete()
        response_data = {"created": created}
        if "wishlist-page" in request.GET:
            response_data["remove"] = True
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
        orderitems = OrderItem.objects.filter(
            user=user, guest_id=guest_id, order=None
        ).select_related("product", "size", "color")
        cart_subtotal = sum([orderitem.get_total for orderitem in orderitems])
        shipping_fee = settings.SHIPPING_FEE * orderitems.count()
        cart_total = cart_subtotal + shipping_fee
        context = {
            "orderitems": orderitems,
            "cart_subtotal": cart_subtotal,
            "shipping_fee": shipping_fee,
            "cart_total": cart_total,
        }
        return render(request, "shop/cart.html", context=context)

    @method_decorator(login_required, name="dispatch")
    def post(self, request):
        # Proceed to checkout
        user = request.user
        coupon_code = request.POST.get("coupon")
        coupon = None
        orderitems = OrderItem.objects.filter(user=user, ordered=False)
        if not orderitems.exists():
            return redirect(reverse("cart"))
        if coupon_code:
            coupon = Coupon.objects.get_or_none(
                code=coupon_code, expiry_date__gt=timezone.now()
            )
            if not coupon:
                sweetify.error(
                    request,
                    title="Error",
                    text="Coupon is invalid/expired",
                    button="OK",
                    timer=3000,
                )
                return redirect(reverse("cart"))
            if Order.objects.filter(user=user, coupon=coupon).exists():
                sweetify.error(
                    request,
                    title="Error",
                    text="You've used this coupon already",
                    button="OK",
                    timer=3000,
                )
                return redirect(reverse("cart"))
        order = Order.objects.create(user=user, coupon=coupon)
        orderitems.update(order=order, ordered=True)
        return redirect(reverse("checkout", kwargs={"tx_ref": order.tx_ref}))


class ToggleCartView(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        user, guest_id = get_user_or_guest_id(request)
        page = request.GET.get("query_page")  # For cart page
        action = request.GET.get("action")  # For cart action
        size = request.GET.get("size")
        color = request.GET.get("color")
        product = get_object_or_404(Product, slug=kwargs["slug"])
        if size:
            size = product.sizes.get_or_none(value=size)
            if not size:
                return JsonResponse({"error": "Invalid size selected"})

        if color:
            color = product.colours.get_or_none(value=color)
            if not color:
                return JsonResponse({"error": "Invalid size selected"})

        orderitem, created = OrderItem.objects.get_or_create(
            user=user,
            guest_id=guest_id,
            ordered=False,
            product=product,
            size=size,
            color=color,
        )
        response_data = {"created": True, "item_id": orderitem.id}
        if not created:
            if action == "add":
                if orderitem.quantity < product.in_stock:
                    orderitem.quantity += 1
                    orderitem.save()
                    response_data["quantity"] = orderitem.quantity
                if orderitem.quantity >= product.in_stock:
                    response_data["item_finished"] = True
            elif action in ["reduce", "remove"]:
                response_data["created"] = False
                if action == "remove" or orderitem.quantity == 1:
                    orderitem.delete()
                    response_data["cart_items_count"] = OrderItem.objects.filter(
                        user=user, guest_id=guest_id, ordered=False
                    ).count()
                    if page == "cart":
                        response_data["remove"] = True
                else:
                    orderitem.quantity -= 1
                    orderitem.save()
                    response_data["quantity"] = orderitem.quantity
        response_data["orderitem_total"] = orderitem.get_total
        return JsonResponse(response_data)


class CheckProductIsInCartView(View):
    def get(self, request, *args, **kwargs):
        user, guest_id = get_user_or_guest_id(request)
        size = request.GET.get("size")
        color = request.GET.get("color")
        slug = kwargs["slug"]  # Assuming you pass the product slug in the URL

        product = get_object_or_404(Product, slug=slug)
        if size:
            size = product.sizes.get_or_none(value=size)
            if not size:
                return JsonResponse({"error": "Invalid size selected"})
        if color:
            color = product.colours.get_or_none(value=color)
            if not color:
                return JsonResponse({"error": "Invalid size selected"})

        is_in_cart = OrderItem.objects.filter(
            user=user, guest_id=guest_id, product=product, size=size, color=color
        ).exists()
        return JsonResponse({"is_in_cart": is_in_cart})


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        order = (
            Order.objects.select_related("coupon")
            .prefetch_related("orderitems", "orderitems__product")
            .get_or_none(user=user, payment_status="PENDING", tx_ref=kwargs["tx_ref"])
        )
        if not order:
            raise Http404("Order Not Found")
        shipping_address = ShippingAddress.objects.order_by("created_at").last()
        form = ShippingAddressForm(instance=shipping_address)
        context = {"order": order, "form": form}
        return render(request, "shop/checkout.html", context=context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        order = Order.objects.prefetch_related(
            "orderitems", "orderitems__product"
        ).get_or_none(user=user, tx_ref=kwargs["tx_ref"])
        if not order:
            raise Http404("Order Not Found")
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get("payment_method")
            new_shipping_address = form.save(commit=False)
            new_shipping_address.user = user
            new_shipping_address.save()
            order.shipping_address = new_shipping_address
            order.payment_method = payment_method
            order.payment_status = "PROCESSING"
            order.save()
            return JsonResponse(
                {
                    "payment_method": payment_method,
                    "pubk": settings.PAYSTACK_PUBLIC_KEY,
                    "tx_ref": order.tx_ref,
                    "amount": order.get_cart_total * 100,
                    "name": user.full_name,
                    "email": user.email,
                }
            )

        context = {"order": order, "form": form}
        return render(request, "shop/checkout_form.html", context=context)


class UpdateOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        order = get_object_or_404(Order, user=user, tx_ref=kwargs["tx_ref"])
        payment_status = request.GET.get("payment_status")

        if payment_status == "CANCELLED":
            order.payment_status = payment_status
            order.save()
        return redirect(reverse("orders"))


class OrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = (
            Order.objects.filter(user=request.user)
            .prefetch_related("orderitems", "orderitems__product")
            .order_by("-created_at")
        )
        context = {"orders": orders}
        return render(request, "shop/orders.html", context)
