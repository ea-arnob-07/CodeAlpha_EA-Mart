from django.urls import path

from . import views


app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),
    path("checkout/", views.checkout, name="checkout"),
    path("account/register/", views.register, name="register"),
    path("account/login/", views.login_view, name="login"),
    path("account/logout/", views.logout_view, name="logout"),
    path("account/profile/", views.profile, name="profile"),
    path("account/orders/", views.order_history, name="order_history"),
    path("account/orders/<str:order_number>/", views.order_detail, name="order_detail"),
    path("order/success/<str:order_number>/", views.order_success, name="order_success"),
]
