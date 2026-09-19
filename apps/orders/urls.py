"""URL-маршруты приложения orders."""

from django.urls import path

from apps.orders.views import (
    CartAddView,
    CartItemDeleteView,
    PartnerOrdersView,
)

app_name = "orders"

urlpatterns = [
    path("partner/orders", PartnerOrdersView.as_view(), name="partner-orders"),
    path("cart", CartAddView.as_view(), name="cart-add"),
    path("cart/<int:item_id>", CartItemDeleteView.as_view(), name="cart-item-delete"),
]
