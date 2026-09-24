"""URL-маршруты приложения orders."""

from django.urls import path

from apps.orders.views import (
    CartItemDeleteView,
    CartView,
    ConfirmOrderView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
    PartnerOrdersView,
)

app_name = "orders"

urlpatterns = [
    path("partner/orders", PartnerOrdersView.as_view(), name="partner-orders"),
    path("cart", CartView.as_view(), name="cart"),
    path("cart/<int:item_id>", CartItemDeleteView.as_view(), name="cart-item-delete"),
    path("confirm", ConfirmOrderView.as_view(), name="confirm-order"),
    path(
        "<int:pk>/status",
        OrderStatusUpdateView.as_view(),
        name="order-status-update",
    ),
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>", OrderDetailView.as_view(), name="order-detail"),
]
