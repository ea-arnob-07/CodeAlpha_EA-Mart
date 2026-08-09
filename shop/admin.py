from django.contrib import admin

from .models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_quantity", "is_featured", "is_active", "updated_at")
    list_filter = ("category", "is_featured", "is_active", "created_at")
    list_editable = ("price", "stock_quantity", "is_featured", "is_active")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("category",)
    inlines = (ProductImageInline,)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "updated_at")
    search_fields = ("user__username", "session_key")
    inlines = (CartItemInline,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "product_price", "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "grand_total", "payment_method", "payment_status", "order_status", "created_at")
    list_filter = ("order_status", "payment_status", "payment_method", "created_at")
    search_fields = ("order_number", "customer_name", "email", "phone", "user__username")
    list_editable = ("payment_status", "order_status")
    readonly_fields = ("order_number", "subtotal", "delivery_fee", "grand_total", "created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = (OrderItemInline,)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "city")
    search_fields = ("user__username", "user__email", "full_name", "phone")


admin.site.site_header = "EA Mart Administration"
admin.site.site_title = "EA Mart Admin"
admin.site.index_title = "Store management"
