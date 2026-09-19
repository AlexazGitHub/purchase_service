"""Сериализаторы приложения products."""

from rest_framework import serializers

from apps.products.models import Product, ProductInfo, ProductParameter
from apps.shops.serializers import CategorySerializer, ShopSerializer


class ProductParameterSerializer(serializers.ModelSerializer):
    """Сериализатор параметра товара (EAV)."""

    name = serializers.CharField(source="parameter.name")

    class Meta:
        model = ProductParameter
        fields = ("name", "value")


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор товара с параметрами."""

    category = CategorySerializer(read_only=True)
    parameters = ProductParameterSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "category", "parameters")


class ProductInfoSerializer(serializers.ModelSerializer):
    """Сериализатор товара в конкретном магазине (для каталога)."""

    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = (
            "id",
            "product",
            "shop",
            "model",
            "price",
            "price_rrc",
            "quantity",
        )
