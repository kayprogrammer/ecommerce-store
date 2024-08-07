from django.contrib import admin

from apps.shop.models import (
    Category,
    Colour,
    Coupon,
    Order,
    OrderItem,
    Product,
    Review,
    ShippingAddress,
    Country,
    Size,
)


class SizeAdmin(admin.ModelAdmin):
    list_display = ("value", "created_at", "updated_at")
    list_filter = list_display


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = list_display


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "desc",
        "price_old",
        "price_current",
        "category",
        "created_at",
        "updated_at",
    )
    list_filter = list_display


class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone_code")
    list_filter = list_display


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "email")
    list_filter = list_display + ("state", "country")


class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "percentage_off", "expiry_date")
    list_filter = list_display
    readonly_fields = ("code", "created_at")


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ("tx_ref",)
    list_display = (
        "user",
        "tx_ref",
        "delivery_status",
        "payment_status",
        "date_delivered",
        "created_at",
    )
    list_filter = list_display


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("user", "guest_id", "product", "quantity", "created_at")
    list_filter = list_display


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at", "updated_at")
    list_filter = list_display


admin.site.register(Size, SizeAdmin)
admin.site.register(Colour, SizeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
