import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


def generate_order_number():
    return f"LC-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:8].upper()}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"{reverse('shop:product_list')}?category={self.slug}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=240)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    previous_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True)
    image_url = models.URLField(blank=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=Decimal("4.7"),
        validators=[MinValueValidator(Decimal("0.0"))],
    )
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["category", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={"slug": self.slug})

    @property
    def in_stock(self):
        return self.is_active and self.stock_quantity > 0

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url

    @property
    def discount_percentage(self):
        if self.previous_price and self.previous_price > self.price:
            return round(((self.previous_price - self.price) / self.previous_price) * 100)
        return 0

    @property
    def savings_amount(self):
        if self.previous_price and self.previous_price > self.price:
            return self.previous_price - self.price
        return Decimal("0.00")


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="products/gallery/", blank=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.alt_text or f"Image for {self.product.name}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.image_url


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=160, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["session_key"],
                condition=~Q(session_key=""),
                name="unique_nonempty_cart_session",
            )
        ]

    def __str__(self):
        owner = self.user.username if self.user else self.session_key[:8]
        return f"Cart {self.pk} ({owner})"

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.select_related("product")), Decimal("0.00"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "product"], name="unique_product_per_cart"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="cart_item_quantity_positive"),
        ]

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity


class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH_ON_DELIVERY = "cod", "Cash on Delivery"

    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PAID = "paid", "Paid"
        REFUNDED = "refunded", "Refunded"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    order_number = models.CharField(max_length=30, unique=True, default=generate_order_number, editable=False)
    customer_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    delivery_address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    order_notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH_ON_DELIVERY)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    order_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    grand_total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["order_status", "-created_at"]),
        ]

    def __str__(self):
        return self.order_number

    def get_absolute_url(self):
        return reverse("shop:order_detail", kwargs={"order_number": self.order_number})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    product_name = models.CharField(max_length=180)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"
