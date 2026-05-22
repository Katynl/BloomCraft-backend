from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Product, Order, OrderItem, Feedback, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "phone", "is_staff", "is_active")
    search_fields = ("username", "email", "phone")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "in_stock",
        "is_new",
        "is_popular",
        "is_gifts",
    )
    list_filter = ("category", "in_stock", "is_new", "is_popular", "is_gifts")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price", "item_total")
    can_delete = False

    def item_total(self, obj):
        if not obj.pk:
            return "-"
        return obj.quantity * obj.price

    item_total.short_description = "Сумма позиции"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "name",
        "phone",
        "email",
        "status",
        "payment_method",
        "pickup_location",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_method", "pickup_location", "created_at")
    search_fields = ("id", "name", "phone", "email", "user__username")
    readonly_fields = ("user", "name", "phone", "email", "comment", "payment_method", "pickup_location", "total", "created_at")
    inlines = [OrderItemInline]

    fieldsets = (
        ("Пользователь", {
            "fields": ("user",)
        }),
        ("Данные получателя", {
            "fields": ("name", "phone", "email", "comment")
        }),
        ("Оплата и самовывоз", {
            "fields": ("payment_method", "pickup_location")
        }),
        ("Статус и сумма", {
            "fields": ("status", "total", "created_at")
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity", "price", "item_total")
    list_filter = ("product",)
    search_fields = ("order__id", "product__name")

    def item_total(self, obj):
        return obj.quantity * obj.price

    item_total.short_description = "Сумма позиции"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")