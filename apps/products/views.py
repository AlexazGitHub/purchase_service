"""API views приложения products."""

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.products.filters import ProductInfoFilter
from apps.products.models import ProductInfo
from apps.products.serializers import ProductInfoSerializer


class ProductListView(ListAPIView):
    """Список товаров с фильтрацией по магазину и категории."""

    queryset = ProductInfo.objects.select_related(
        "product",
        "product__category",
        "shop",
    ).prefetch_related("product__parameters__parameter")
    serializer_class = ProductInfoSerializer
    permission_classes = (AllowAny,)
    filterset_class = ProductInfoFilter


class ProductDetailView(RetrieveAPIView):
    """Детальная карточка товара в конкретном магазине."""

    queryset = ProductInfo.objects.select_related(
        "product",
        "product__category",
        "shop",
    ).prefetch_related("product__parameters__parameter")
    serializer_class = ProductInfoSerializer
    permission_classes = (AllowAny,)
