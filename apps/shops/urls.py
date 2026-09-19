"""URL-маршруты приложения shops."""

from django.urls import path

from apps.shops.views import PartnerUpdateView

app_name = "shops"

urlpatterns = [
    path("partner/update", PartnerUpdateView.as_view(), name="partner-update"),
]
