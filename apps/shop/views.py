from django.http import Http404, JsonResponse, HttpResponse
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.accounts.mixins import LoginRequiredMixin
from apps.accounts.senders import EmailUtil
from apps.common.utils import REVIEWS_AND_RATING_ANNOTATION
from .forms import ReviewForm, ShippingAddressForm
from .models import (
    Category,
    Coupon,
    Order,
    OrderItem,
    Product,
    Review,
    ShippingAddress,
    Wishlist,
)

from .utils import (
    colour_size_filter_products,
    generic_products_ctx,
    get_user_or_guest_id,
    update_product_in_stock,
    verify_webhook_signature,
)
import sweetify, hashlib, hmac, json, decimal

PRODUCTS_PER_PAGE = 15


class ProductsView(ListView):
    model = Product
    paginate_by = PRODUCTS_PER_PAGE
    template_name = "shop/products.html"
    context_object_name = "products"

    def get_queryset(self):
        name_filter = self.request.GET.get("name")
        products = Product.objects.annotate(**REVIEWS_AND_RATING_ANNOTATION).filter(
            in_stock__gt=0
        )
        if name_filter:
            products = products.filter(name__icontains=name_filter)
        return colour_size_filter_products(
            products.order_by("-created_at"),
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
    def get_product(self, slug):
        products = (
            Product.objects.filter(in_stock__gt=0)
            .select_related("category")
            .annotate(**REVIEWS_AND_RATING_ANNOTATION)
        )
        product = products.prefetch_related("sizes", "colours", "reviews").get_or_none(
            slug=slug
        )
        if not product:
            raise Http404("Product does not exist!")
        related_products = products.filter(category_id=product.category_id).exclude(
            id=product.id
        )[:10]
        reviews = product.reviews.order_by("-rating")
        return product, related_products, reviews

    def get(self, request, *args, **kwargs):
        user = request.user
        product, related_products, reviews = self.get_product(kwargs["slug"])
        review = None
        if user.is_authenticated:
            review = Review.objects.get_or_none(user=user, product=product)
        form = ReviewForm(instance=review)
        context = {
            "product": product,
            "review": review,
            "reviews": reviews,
            "related_products": related_products,
            "form": form,
        }
        return render(request, "shop/product.html", context=context)

    @method_decorator(login_required, name="dispatch")
    def post(self, request, *args, **kwargs):
        user = request.user
        slug = kwargs["slug"]
        product, related_products, reviews = self.get_product(slug)
        review = Review.objects.get_or_none(user=user, product=product)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.product = product
            instance.user = user
            instance.save()
            sweetify.success(request, title="Success", text="Review sent", timer=2500, button="OK")
            return redirect(reverse("product", kwargs={"slug": slug}))
        context = {
            "product": product,
            "review": review,
            "reviews": reviews,
            "related_products": related_products,
            "form": form,
        }
        return render(request, "shop/product.html", context=context)


class WishlistView(ListView):
    def get(self, request):
        user, guest_id = get_user_or_guest_id(self.request)
        products = (
            Product.objects.filter(
                in_stock__gt=0, wishlist__user=user, wishlist__guest_id=guest_id
            )
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
        product = get_object_or_404(Product, slug=kwargs["slug"], in_stock__gt=0)
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
            Product.objects.filter(category=category, in_stock__gt=0)
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
        orderitems = OrderItem.objects.filter(user=user, order=None)
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
        orderitems.update(order=order)
        return redirect(reverse("checkout", kwargs={"tx_ref": order.tx_ref}))


class ToggleCartView(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        user, guest_id = get_user_or_guest_id(request)
        page = request.GET.get("query_page")  # For cart page
        action = request.GET.get("action")  # For cart action
        size = request.GET.get("size")
        color = request.GET.get("color")
        product = get_object_or_404(Product, slug=kwargs["slug"], in_stock__gt=0)
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
            order_id=None,
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
                        user=user, guest_id=guest_id, order=None
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
                return JsonResponse({"error": "Invalid color selected"})

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
        shipping_address = (
            ShippingAddress.objects.filter(user=user).order_by("created_at").last()
        )
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
                    "tx_ref": order.tx_ref,
                    "amount": (
                        order.get_cart_total * 100
                        if payment_method == "PAYSTACK"
                        else order.get_cart_total
                    ),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
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

        if payment_status in ["CANCELLED", "FAILED"]:
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


@csrf_exempt
def paystack_webhook(request):
    # retrive the payload from the request body
    payload = request.body
    # signature header to to verify the request is from paystack
    sig_header = request.headers["x-paystack-signature"]
    body, event = None, None

    try:
        # sign the payload with `HMAC SHA512`
        hash = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            payload,
            digestmod=hashlib.sha512,
        ).hexdigest()
        # compare our signature with paystacks signature
        if hash == sig_header:
            # if signature matches,
            # proceed to retrive event status from payload
            body_unicode = payload.decode("utf-8")
            body = json.loads(body_unicode)
            # event status
            event = body["event"]
        else:
            raise Exception
    except Exception as e:
        return HttpResponse(status=400)

    if event == "charge.success":
        data = body["data"]
        if (data["status"] == "success") and (data["gateway_response"] == "Successful"):
            order = (
                Order.objects.prefetch_related("orderitems")
                .prefetch_related("orderitems__product")
                .get_or_none(tx_ref=data["reference"])
            )
            amount_paid = data["amount"] / 100
            if not order:
                customer = data["customer"]
                name = f"{customer.get('first_name', "John")} {customer.get("last_name", "Doe")}"
                email = customer.get("email")
                EmailUtil.send_payment_failed_email(request, name, email, amount_paid)
                return HttpResponse(status=200)
            amount_payable = order.get_cart_total
            user = order.user
            if amount_paid < amount_payable:
                # You made an invalid payment
                EmailUtil.send_payment_failed_email(
                    request, user.full_name, user.email, amount_paid
                )
                order.payment_status = "FAILED"
                order.save()
                return HttpResponse(status=200)

            order.payment_status = "SUCCESSFUL"
            order.save()
            update_product_in_stock(order.orderitems.all())
            # Send email
            EmailUtil.send_payment_success_email(
                request, user.full_name, user.email, amount_payable
            )
        else:
            return HttpResponse(status=200)
    return HttpResponse(status=200)


@csrf_exempt
def paypal_webhook(request):
    payload = request.body
    headers = request.headers
    # Verify webhook signature
    transmission_id = headers.get("Paypal-Transmission-Id")
    transmission_time = headers.get("Paypal-Transmission-Time")
    cert_url = headers.get("Paypal-Cert-Url")
    auth_algo = headers.get("Paypal-Auth-Algo")
    transmission_sig = headers.get("Paypal-Transmission-Sig")
    webhook_id = settings.PAYPAL_WEBHOOK_ID
    valid_sig = verify_webhook_signature(
        transmission_sig,
        transmission_id,
        transmission_time,
        webhook_id,
        payload.decode("utf-8"),
        cert_url,
        auth_algo,
    )
    if valid_sig:
        event = json.loads(payload)

        if event["event_type"] == "CHECKOUT.ORDER.APPROVED":
            # Handle payment completed event
            resource = event["resource"]
            purchase_unit = resource["purchase_units"][0]
            amount_paid = decimal.Decimal(purchase_unit["amount"]["value"])
            order = (
                Order.objects.prefetch_related("orderitems")
                .prefetch_related("orderitems__product")
                .get_or_none(tx_ref=purchase_unit["reference_id"])
            )
            if not order:
                return HttpResponse(status=200)
            if order.payment_status != "SUCCESSFUL":
                user = order.user
                amount_payable = order.get_cart_total
                if amount_paid < amount_payable:
                    # You made an invalid payment
                    EmailUtil.send_payment_failed_email(
                        request, user.full_name, user.email, amount_paid
                    )
                    order.payment_status = "FAILED"
                    order.save()
                    return HttpResponse(status=200)

                order.payment_status = "SUCCESSFUL"
                order.save()

                update_product_in_stock(order.orderitems.all())
                # Send email
                EmailUtil.send_payment_success_email(
                    request, user.full_name, user.email, amount_payable
                )
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=200)
