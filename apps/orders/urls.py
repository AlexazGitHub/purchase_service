"""URL-маршруты приложения orders."""

from django.urls import path

from apps.orders.views import PartnerOrdersView

app_name = "orders"

urlpatterns = [
    path("partner/orders", PartnerOrdersView.as_view(), name="partner-orders"),
]
