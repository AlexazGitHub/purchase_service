"""URL-маршруты приложения orders."""

from django.urls import path

from apps.orders.views import CartItemDeleteView, CartView, PartnerOrdersView

app_name = "orders"

urlpatterns = [
    path("partner/orders", PartnerOrdersView.as_view(), name="partner-orders"),
    path("cart", CartView.as_view(), name="cart"),
    path("cart/<int:item_id>", CartItemDeleteView.as_view(), name="cart-item-delete"),
]
