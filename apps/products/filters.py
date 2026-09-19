"""Фильтры приложения products."""

import django_filters

from apps.products.models import ProductInfo


class ProductInfoFilter(django_filters.FilterSet):
    """Фильтр каталога товаров по магазину и категории."""

    shop_id = django_filters.NumberFilter(field_name="shop_id")
    category_id = django_filters.NumberFilter(
        field_name="product__category_id",
    )

    class Meta:
        model = ProductInfo
        fields = ("shop_id", "category_id")
