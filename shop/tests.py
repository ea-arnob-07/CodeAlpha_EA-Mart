from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cart, CartItem, Category, Order, Product


User = get_user_model()


class StoreFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Technology", slug="technology")
        self.product = Product.objects.create(
            category=self.category,
            name="Arc Wireless Headphones",
            slug="arc-wireless-headphones",
            short_description="Immersive sound for focused days.",
            description="A detailed product description.",
            price=Decimal("1000.00"),
            previous_price=Decimal("1200.00"),
            stock_quantity=5,
            is_featured=True,
        )
        self.user = User.objects.create_user(
            username="shopper",
            email="shopper@example.com",
            password="StrongPass987!",
            first_name="Luxe",
            last_name="Shopper",
        )

    def test_home_and_product_pages_render(self):
        home_response = self.client.get(reverse("shop:home"))
        detail_response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, self.product.name)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Developed by Estiuk Arafat Arnob")

    def test_registration_creates_authenticated_user(self):
        response = self.client.post(
            reverse("shop:register"),
            {
                "first_name": "New",
                "last_name": "Member",
                "username": "newmember",
                "email": "new@example.com",
                "password1": "ExcellentPass987!",
                "password2": "ExcellentPass987!",
            },
        )
        self.assertRedirects(response, reverse("shop:home"))
        self.assertTrue(User.objects.filter(username="newmember").exists())
        self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(username="newmember").pk)

    def test_guest_can_add_and_update_cart(self):
        add_response = self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 2})
        self.assertEqual(add_response.status_code, 302)
        item = CartItem.objects.get(product=self.product)
        self.assertEqual(item.quantity, 2)

        update_response = self.client.post(reverse("shop:cart_update", args=[item.pk]), {"quantity": 3})
        self.assertRedirects(update_response, reverse("shop:cart_detail"))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_guest_cart_merges_after_login(self):
        self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 2})
        response = self.client.post(
            reverse("shop:login"),
            {"username": "shopper", "password": "StrongPass987!"},
        )
        self.assertRedirects(response, reverse("shop:home"))
        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.items.get(product=self.product).quantity, 2)
        self.assertFalse(Cart.objects.filter(user__isnull=True, items__product=self.product).exists())

    def test_cart_rejects_quantity_above_stock(self):
        response = self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 6})
        self.assertRedirects(response, self.product.get_absolute_url())
        self.assertFalse(CartItem.objects.filter(product=self.product).exists())

    def test_checkout_requires_login(self):
        response = self.client.get(reverse("shop:checkout"))
        expected = f"{reverse('shop:login')}?next={reverse('shop:checkout')}"
        self.assertRedirects(response, expected)

    def test_checkout_creates_order_and_calculates_totals_server_side(self):
        self.client.login(username="shopper", password="StrongPass987!")
        self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 2})
        response = self.client.post(
            reverse("shop:checkout"),
            {
                "customer_name": "Luxe Shopper",
                "email": "shopper@example.com",
                "phone": "01700000000",
                "delivery_address": "House 10, Road 2",
                "city": "Dhaka",
                "postal_code": "1207",
                "order_notes": "Call before delivery",
                "payment_method": "cod",
                "subtotal": "1.00",
                "grand_total": "1.00",
            },
        )
        order = Order.objects.get(user=self.user)
        self.assertRedirects(response, reverse("shop:order_success", args=[order.order_number]))
        self.assertEqual(order.subtotal, Decimal("2000.00"))
        self.assertEqual(order.delivery_fee, Decimal("120.00"))
        self.assertEqual(order.grand_total, Decimal("2120.00"))
        self.assertEqual(order.items.get().line_total, Decimal("2000.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)
        self.assertFalse(self.user.shopping_cart.items.exists())

    def test_free_delivery_threshold_is_applied(self):
        self.product.price = Decimal("1600.00")
        self.product.save()
        self.client.login(username="shopper", password="StrongPass987!")
        self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 2})
        self.client.post(
            reverse("shop:checkout"),
            {
                "customer_name": "Luxe Shopper",
                "email": "shopper@example.com",
                "phone": "01700000000",
                "delivery_address": "House 10, Road 2",
                "city": "Dhaka",
                "postal_code": "1207",
                "order_notes": "",
                "payment_method": "cod",
            },
        )
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.subtotal, Decimal("3200.00"))
        self.assertEqual(order.delivery_fee, Decimal("0.00"))
        self.assertEqual(order.grand_total, Decimal("3200.00"))

    def test_checkout_revalidates_stock(self):
        self.client.login(username="shopper", password="StrongPass987!")
        self.client.post(reverse("shop:cart_add", args=[self.product.pk]), {"quantity": 4})
        self.product.stock_quantity = 2
        self.product.save()
        response = self.client.post(
            reverse("shop:checkout"),
            {
                "customer_name": "Luxe Shopper",
                "email": "shopper@example.com",
                "phone": "01700000000",
                "delivery_address": "House 10, Road 2",
                "city": "Dhaka",
                "postal_code": "1207",
                "order_notes": "",
                "payment_method": "cod",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no longer has the requested quantity")
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_user_cannot_view_another_users_order(self):
        order = Order.objects.create(
            user=self.user,
            customer_name="Luxe Shopper",
            email="shopper@example.com",
            phone="01700000000",
            delivery_address="Dhaka",
            city="Dhaka",
            postal_code="1207",
            subtotal=Decimal("1000.00"),
            delivery_fee=Decimal("120.00"),
            grand_total=Decimal("1120.00"),
        )
        other = User.objects.create_user(username="other", password="OtherPass987!")
        self.client.force_login(other)
        response = self.client.get(order.get_absolute_url())
        self.assertEqual(response.status_code, 404)
