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


class AddToCartSerializer(serializers.Serializer):
    """Сериализатор для добавления товара в корзину."""

    product_id = serializers.IntegerField()
    shop_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)


class CartItemSerializer(serializers.ModelSerializer):
    """Позиция корзины."""

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )
    shop_name = serializers.CharField(
        source="shop.name",
        read_only=True,
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_name",
            "shop_name",
            "quantity",
            "price",
            "total",
        )

    def get_total(self, item):
        """Посчитать сумму по позиции (цена x количество)."""
        return item.price * item.quantity


class CartSerializer(serializers.ModelSerializer):
    """Корзина пользователя со списком позиций и итоговой суммой."""

    items = CartItemSerializer(many=True, read_only=True)
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("id", "status", "items", "total_sum")

    def get_total_sum(self, order):
        """Посчитать общую сумму корзины по всем позициям."""
        return sum(item.price * item.quantity for item in order.items.all())


class ConfirmOrderSerializer(serializers.Serializer):
    """Сериализатор подтверждения заказа."""

    contact_id = serializers.IntegerField()


class OrderSerializer(serializers.ModelSerializer):
    """Оформленный заказ пользователя со списком позиций."""

    items = CartItemSerializer(many=True, read_only=True)
    total_sum = serializers.SerializerMethodField()
    contact_id = serializers.IntegerField(source="contact.id", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "created_at",
            "contact_id",
            "items",
            "total_sum",
        )

    def get_total_sum(self, order):
        """Посчитать общую сумму заказа по всем позициям."""
        return sum(item.price * item.quantity for item in order.items.all())


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Сериализатор смены статуса заказа."""

    status = serializers.ChoiceField(choices=Order.Status.choices)
