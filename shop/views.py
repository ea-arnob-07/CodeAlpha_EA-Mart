from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .cart import cart_totals, get_cart, merge_guest_cart
from .forms import CheckoutForm, LoginForm, ProfileForm, RegistrationForm, UserUpdateForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product, UserProfile


class StockError(Exception):
    pass


def _safe_next_url(request, fallback="shop:home"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return reverse(fallback)


def _cart_json(cart, message):
    totals = cart_totals(cart)
    return JsonResponse(
        {
            "ok": True,
            "message": message,
            "cart_count": cart.item_count,
            "subtotal": f"{totals['subtotal']:.2f}",
            "delivery_fee": f"{totals['delivery_fee']:.2f}",
            "grand_total": f"{totals['grand_total']:.2f}",
        }
    )


def home(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    context = {
        "featured_products": products.filter(is_featured=True)[:8],
        "latest_products": products[:8],
        "categories": Category.objects.all()[:6],
        "hero_product": products.filter(is_featured=True).first() or products.first(),
    }
    return render(request, "shop/home.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "newest")

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except (ValueError, ArithmeticError):
        messages.warning(request, "Please enter a valid price range.")

    ordering = {
        "newest": "-created_at",
        "price_low": "price",
        "price_high": "-price",
        "name": "name",
    }
    products = products.order_by(ordering.get(sort, "-created_at"))
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "shop/product_list.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "query": query,
            "selected_category": category_slug,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("gallery_images"),
        slug=slug,
        is_active=True,
    )
    related_products = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .select_related("category")[:4]
    )
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "related_products": related_products},
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart = get_cart(request)
    item = CartItem.objects.filter(cart=cart, product=product).first()
    desired_quantity = quantity if item is None else item.quantity + quantity
    if product.stock_quantity < desired_quantity:
        message = f"Only {product.stock_quantity} item(s) are available."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "message": message}, status=400)
        messages.error(request, message)
        return redirect(product.get_absolute_url())

    if item is None:
        CartItem.objects.create(cart=cart, product=product, quantity=desired_quantity)
    else:
        item.quantity = desired_quantity
        item.save(update_fields=["quantity", "updated_at"])
    message = f"{product.name} added to your cart."
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return _cart_json(cart, message)
    messages.success(request, message)
    return redirect(request.POST.get("next") or "shop:cart_detail")


def cart_detail(request):
    cart = get_cart(request)
    items = cart.items.select_related("product", "product__category")
    return render(request, "shop/cart_detail.html", {"cart": cart, "cart_items": items, **cart_totals(cart)})


@require_POST
def cart_update(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart=cart)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        product_name = item.product.name
        item.delete()
        message = f"{product_name} removed from your cart."
    elif quantity > item.product.stock_quantity:
        message = f"Only {item.product.stock_quantity} item(s) are available."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "message": message}, status=400)
        messages.error(request, message)
        return redirect("shop:cart_detail")
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])
        message = "Cart quantity updated."

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return _cart_json(cart, message)
    messages.success(request, message)
    return redirect("shop:cart_detail")


@require_POST
def cart_remove(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart=cart)
    product_name = item.product.name
    item.delete()
    message = f"{product_name} removed from your cart."
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return _cart_json(cart, message)
    messages.success(request, message)
    return redirect("shop:cart_detail")


@require_POST
def cart_clear(request):
    cart = get_cart(request)
    cart.items.all().delete()
    messages.success(request, "Your cart is now empty.")
    return redirect("shop:cart_detail")


def register(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    old_session_key = request.session.session_key
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        merge_guest_cart(user, old_session_key)
        messages.success(request, f"Welcome to EA Mart, {user.first_name or user.username}!")
        return redirect(_safe_next_url(request))
    return render(request, "accounts/register.html", {"form": form, "next": request.GET.get("next", "")})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:home")
    old_session_key = request.session.session_key
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        merge_guest_cart(user, old_session_key)
        messages.success(request, f"Welcome back, {user.first_name or user.username}.")
        return redirect(_safe_next_url(request))
    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been signed out securely.")
    return redirect("shop:home")


@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("shop:profile")
    recent_orders = request.user.orders.prefetch_related("items")[:3]
    return render(
        request,
        "accounts/profile.html",
        {"user_form": user_form, "profile_form": profile_form, "recent_orders": recent_orders},
    )


@login_required
def checkout(request):
    cart = get_cart(request)
    cart_items = list(cart.items.select_related("product"))
    if not cart_items:
        messages.info(request, "Add something to your cart before checkout.")
        return redirect("shop:product_list")

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    initial = {
        "customer_name": profile.full_name or request.user.get_full_name(),
        "email": request.user.email,
        "phone": profile.phone,
        "delivery_address": profile.address,
        "city": profile.city,
        "postal_code": profile.postal_code,
    }
    form = CheckoutForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                locked_cart = Cart.objects.select_for_update().get(pk=cart.pk)
                locked_items = list(locked_cart.items.select_related("product"))
                if not locked_items:
                    raise StockError("Your cart is empty.")

                subtotal = Decimal("0.00")
                order_item_data = []
                for cart_item in locked_items:
                    product = Product.objects.select_for_update().get(pk=cart_item.product_id)
                    if not product.is_active or product.stock_quantity < cart_item.quantity:
                        raise StockError(f"{product.name} no longer has the requested quantity in stock.")
                    line_total = product.price * cart_item.quantity
                    subtotal += line_total
                    order_item_data.append((product, cart_item.quantity, line_total))

                totals = cart_totals(locked_cart)
                totals["subtotal"] = subtotal
                totals["delivery_fee"] = Decimal("0.00") if subtotal >= Decimal("3000.00") else Decimal("120.00")
                totals["grand_total"] = totals["subtotal"] + totals["delivery_fee"]

                order = form.save(commit=False)
                order.user = request.user
                order.subtotal = totals["subtotal"]
                order.delivery_fee = totals["delivery_fee"]
                order.grand_total = totals["grand_total"]
                order.save()

                order_items = []
                for product, quantity, line_total in order_item_data:
                    order_items.append(
                        OrderItem(
                            order=order,
                            product=product,
                            product_name=product.name,
                            product_price=product.price,
                            quantity=quantity,
                            line_total=line_total,
                        )
                    )
                    product.stock_quantity -= quantity
                    product.save(update_fields=["stock_quantity", "updated_at"])
                OrderItem.objects.bulk_create(order_items)
                locked_cart.items.all().delete()

                profile.full_name = order.customer_name
                profile.phone = order.phone
                profile.address = order.delivery_address
                profile.city = order.city
                profile.postal_code = order.postal_code
                profile.save()
        except StockError as exc:
            form.add_error(None, str(exc))
        else:
            messages.success(request, "Your order has been placed successfully.")
            return redirect("shop:order_success", order_number=order.order_number)

    return render(
        request,
        "shop/checkout.html",
        {"form": form, "cart_items": cart_items, **cart_totals(cart)},
    )


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.prefetch_related("items", "items__product"),
        order_number=order_number,
        user=request.user,
    )
    return render(request, "shop/order_detail.html", {"order": order})


def custom_404(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_500(request):
    return render(request, "errors/500.html", status=500)
