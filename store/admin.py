from django.db.models import Count
from django.contrib import admin
from .models import (
    Customer,
    Product,
    Address,
    Cart,
    CartItem,
    OrderItem,
    Order,
    Collection,
    Promotion,
)
from django.urls import reverse
from django.utils.html import format_html, urlencode


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    autocomplete_fields = ["collection"]
    list_display = ["title", "unit_price", "inventory_status", "collection_name"]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_filter = ["collection", "last_update"]
    list_select_related = ["collection"]

    def collection_name(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": f"{collection.id}"})
        )
        return format_html('<a  href="{}">{}</a>', url, collection.products_count)


    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user__first_name", "user__last_name", "membership"]
    list_editable = ["membership"]
    list_per_page = 10
    search_fields = ["first_name__istartswith", "last_name__istartswith"]
    list_select_related=["user"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]


admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(Promotion)
