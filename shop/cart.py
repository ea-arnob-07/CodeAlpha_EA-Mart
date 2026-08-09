from decimal import Decimal

from django.db import transaction

from .models import Cart, CartItem


FREE_DELIVERY_THRESHOLD = Decimal("3000.00")
STANDARD_DELIVERY_FEE = Decimal("120.00")


def ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def merge_guest_cart(user, session_key):
    if not session_key:
        return Cart.objects.get_or_create(user=user, defaults={"session_key": ""})[0]

    with transaction.atomic():
        user_cart, _ = Cart.objects.select_for_update().get_or_create(user=user, defaults={"session_key": ""})
        guest_cart = (
            Cart.objects.select_for_update()
            .filter(user__isnull=True, session_key=session_key)
            .first()
        )
        if not guest_cart or guest_cart.pk == user_cart.pk:
            return user_cart

        for guest_item in guest_cart.items.select_related("product"):
            item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=guest_item.product,
                defaults={"quantity": min(guest_item.quantity, guest_item.product.stock_quantity)},
            )
            if not created:
                item.quantity = min(
                    item.quantity + guest_item.quantity,
                    guest_item.product.stock_quantity,
                )
                if item.quantity > 0:
                    item.save(update_fields=["quantity", "updated_at"])
        guest_cart.delete()
        return user_cart


def get_cart(request):
    session_key = ensure_session_key(request)
    if request.user.is_authenticated:
        return merge_guest_cart(request.user, session_key)
    cart, _ = Cart.objects.get_or_create(user=None, session_key=session_key)
    return cart


def delivery_fee_for(subtotal):
    if subtotal <= 0 or subtotal >= FREE_DELIVERY_THRESHOLD:
        return Decimal("0.00")
    return STANDARD_DELIVERY_FEE


def cart_totals(cart):
    subtotal = cart.subtotal
    delivery_fee = delivery_fee_for(subtotal)
    return {
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "grand_total": subtotal + delivery_fee,
        "free_delivery_remaining": max(FREE_DELIVERY_THRESHOLD - subtotal, Decimal("0.00")),
    }
