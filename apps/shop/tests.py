from django.test import TestCase
from django.conf import settings
from django.http import HttpResponseNotFound
from django.urls import reverse

from apps.common.utils import TestUtil

from apps.shop.models import OrderItem, Order
from apps.shop.forms import ShippingAddressForm, ReviewForm

settings.TESTING = True


class TestShop(TestCase):
    all_products_url = "/shop/"
    wishlist_url = "/shop/wishlist/"
    toggle_wishlist_url = "/shop/toggle-wishlist"
    categories_url = "/shop/categories"
    cart_url = "/shop/cart/"

    maxDiff = None

    def setUp(self):
        user = TestUtil.new_user()
        self.user = user
        self.product = TestUtil.create_product()
        self.client.login(email=self.user.email, password="testpassword")

    def test_all_products_view(self):
        product = self.product
        # Verify that all products are retrieved successfully
        response = self.client.get(self.all_products_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/products.html")
        self.assertQuerySetEqual(response.context["products"], [product])

    def test_product_view(self):
        product = self.product

        # Verify that a particular product retrieval fails with an invalid slug
        response = self.client.get(f"{self.all_products_url}products/invalid_slug/")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponseNotFound)

        # Verify that a product is retrieved successfully
        response = self.client.get(f"{self.all_products_url}products/{product.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/product.html")
        self.assertIsInstance(response.context["form"], ReviewForm)
        self.assertEqual(response.context["product"], product)

    def test_submit_review(self):
        product = self.product
        url = f"{self.all_products_url}products/{product.slug}/"
        response = self.client.post(
            url,
            {
                "rating": 3,
                "text": "Whatever this rating is about man",
            },
        )
        self.assertRedirects(
            response,
            url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_wishlist_view(self):
        product = self.product
        TestUtil.create_wishlist(self.user, product)

        # Verify that all products in wishlist are retrieved successfully
        response = self.client.get(self.wishlist_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/products.html")
        self.assertQuerySetEqual(response.context["products"], [product])

    def test_toggle_wishlist_view(self):
        product = self.product

        # Verify that wishlist toggles properly
        response = self.client.get(f"{self.toggle_wishlist_url}/{product.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"created": True})

    def test_all_products_by_category_view(self):
        product = self.product
        # Verify that all products in a category are retrieved successfully
        response = self.client.get(f"{self.categories_url}/{product.category.slug}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/products.html")
        self.assertQuerySetEqual(response.context["products"], [product])

    def test_cart_view(self):
        product = self.product
        orderitem = TestUtil.create_orderitem(self.user, product)
        # Verify that all cart items are retrieved successfully
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/cart.html")
        self.assertQuerySetEqual(response.context["orderitems"], [orderitem])
        self.assertEqual(response.context["shipping_fee"], settings.SHIPPING_FEE)
        self.assertEqual(response.context["cart_subtotal"], orderitem.get_total)
        self.assertEqual(
            response.context["cart_total"], orderitem.get_total + settings.SHIPPING_FEE
        )

    def test_proceed_to_checkout_view(self):
        coupon = TestUtil.create_coupon()
        TestUtil.create_orderitem(self.user, self.product)

        # Verify the response is correct for invalid coupon
        response = self.client.post(self.cart_url, {"coupon": "INVALID COUPON"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            self.cart_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        # Check if the order is not created
        self.assertFalse(Order.objects.filter(user=self.user).exists())

        # Verify the response is correct for valid coupon
        response = self.client.post(self.cart_url, {"coupon": coupon.code})
        self.assertEqual(response.status_code, 302)
        # Check if the order is created
        order = Order.objects.filter(user=self.user, coupon=coupon).first()
        self.assertIsNotNone(order)
        # Check if the order items are updated
        self.assertTrue(OrderItem.objects.filter(order=order).exists())

        self.assertRedirects(
            response,
            reverse("checkout", kwargs={"tx_ref": order.tx_ref}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_toggle_cart_view(self):
        product = self.product

        # Verify that cart toggles properly
        response = self.client.get(f"/shop/toggle-cart/{product.slug}/?action=add")
        self.assertEqual(response.status_code, 200)
        orderitem = OrderItem.objects.filter(user=self.user).first()
        self.assertEqual(
            response.json(),
            {
                "created": True,
                "item_id": str(orderitem.id),
                "orderitem_total": str(orderitem.get_total),
            },
        )

    def test_check_product_is_in_cart_view(self):
        product = self.product
        TestUtil.create_orderitem(self.user, product)

        # Verify that product is in cart
        response = self.client.get(
            f"/shop/check-product-is-in-cart/{product.slug}/?size=M&color=Black"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"is_in_cart": True})

    def test_checkout_view(self):
        order = TestUtil.create_order(self.user)

        # Verify that a particular order retrieval fails with an tx ref
        response = self.client.get("/shop/checkout/invalid_txref/")
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response, HttpResponseNotFound)

        # Verify that order is valid
        response = self.client.get(f"/shop/checkout/{order.tx_ref}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/checkout.html")
        self.assertIsInstance(response.context["form"], ShippingAddressForm)
        self.assertEqual(response.context["order"], order)

        country = TestUtil.create_country()

        # POST
        response = self.client.post(
            f"/shop/checkout/{order.tx_ref}/",
            {
                "full_name": "Test Orderer",
                "email": "test_orderer@example.com",
                "phone": "+23456565656",
                "address": "Whatever Address",
                "city": "Whatever City",
                "state": "Whatever State",
                "country": country.id,
                "zipcode": 123445,
                "payment_method": "PAYSTACK",
            },
        )
        self.assertEqual(response.status_code, 200)
        # Parse the JSON response
        response_data = response.json()

        self.assertIn("success", response_data)
        self.assertEqual(response_data["success"], True)

    def test_update_order_view(self):
        order = TestUtil.create_order(self.user)
        # Verify the response is correct
        response = self.client.get(
            f"/shop/orders/{order.tx_ref}/update/?payment_status=CANCELLED"
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("orders"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_orders_view(self):
        order = TestUtil.create_order(self.user)
        # Verify that all orders are retrieved successfully
        response = self.client.get("/shop/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "shop/orders.html")
        self.assertQuerySetEqual(response.context["orders"], [order])
