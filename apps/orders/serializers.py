"""Сериализаторы приложения orders."""

from rest_framework import serializers

from apps.orders.models import Order, OrderItem


class OrderItemForPartnerSerializer(serializers.ModelSerializer):
    """Позиция заказа в разрезе конкретного магазина-партнёра."""

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = ("product_name", "quantity", "price")


class OrderForPartnerSerializer(serializers.ModelSerializer):
    """Заказ с позициями, отфильтрованными по магазину партнёра."""

    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "status", "created_at", "items")

    def get_items(self, order):
        """Вернуть только позиции заказа, относящиеся к текущему магазину."""
        shop = self.context["shop"]
        items = order.items.filter(shop=shop)
        return OrderItemForPartnerSerializer(items, many=True).data