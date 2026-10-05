from django.contrib import admin
from django.utils.html import format_html
from .models import Product, CartItem, Order, OrderItem, Address


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'gender', 'category', 'price', 'rating')
    list_filter = ('gender', 'category')
    search_fields = ('name',)
    readonly_fields = ('image_preview',)
    fields = ('name', 'gender', 'category', 'price', 'rating', 'badge', 'image_file', 'image_preview', 'image')

    @admin.display(description='Photo')
    def thumbnail(self, obj):
        if obj.display_image:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.display_image)
        return "—"

    @admin.display(description='Current image')
    def image_preview(self, obj):
        if obj and obj.display_image:
            return format_html('<img src="{}" style="max-height:200px; border-radius:10px;">', obj.display_image)
        return "No image yet — save the product first, or add an image below."


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('user',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'payment_status', 'razorpay_payment_id', 'created_at')
    list_filter = ('created_at', 'payment_status')
    inlines = [OrderItemInline]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'pincode', 'phone')
    search_fields = ('user__username', 'full_name', 'city', 'pincode')
