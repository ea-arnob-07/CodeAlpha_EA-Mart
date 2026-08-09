from .cart import FREE_DELIVERY_THRESHOLD, get_cart
from .models import Category


def store_context(request):
    cart = get_cart(request)
    return {
        "nav_categories": Category.objects.all()[:6],
        "cart_item_count": cart.item_count,
        "free_delivery_threshold": FREE_DELIVERY_THRESHOLD,
    }
