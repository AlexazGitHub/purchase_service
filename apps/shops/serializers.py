"""Сериализаторы приложения shops."""

from rest_framework import serializers

from apps.shops.models import Category, Shop


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории товаров."""

    class Meta:
        model = Category
        fields = ("id", "name")


class ShopSerializer(serializers.ModelSerializer):
    """Сериализатор магазина."""

    class Meta:
        model = Shop
        fields = ("id", "name", "state")
