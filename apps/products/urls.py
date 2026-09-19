"""URL-маршруты приложения products."""

from django.urls import path

from apps.products.views import ProductDetailView, ProductListView

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>", ProductDetailView.as_view(), name="product-detail"),
]
