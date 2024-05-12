from django.contrib import admin

from apps.shop.models import Category, Colour, Product, Review, Size

class SizeAdmin(admin.ModelAdmin):
    list_display = ("value", "created_at", "updated_at")
    list_filter = list_display

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = list_display

class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "desc", "price_old", "price_current", "category", "created_at", "updated_at")
    list_filter = list_display

class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at", "updated_at")
    list_filter = list_display

admin.site.register(Size, SizeAdmin)
admin.site.register(Colour, SizeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)

