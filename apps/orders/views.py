"""API views приложения orders."""

from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderForPartnerSerializer, CartSerializer
from apps.shops.models import Shop
from apps.users.permissions import IsShopUser
from apps.orders.serializers import AddToCartSerializer
from apps.products.models import ProductInfo


class PartnerOrdersView(ListAPIView):
    """Список заказов, содержащих товары магазина текущего пользователя."""

    serializer_class = OrderForPartnerSerializer
    permission_classes = (IsAuthenticated, IsShopUser)

    def get_queryset(self):
        """Вернуть оформленные заказы, содержащие товары этого магазина."""
        shop = Shop.objects.get(user=self.request.user)
        return (
            Order.objects.filter(items__shop=shop)
            .exclude(status=Order.Status.BASKET)
            .distinct()
        )

    def get_serializer_context(self):
        """Добавить магазин пользователя в контекст сериализатора."""
        context = super().get_serializer_context()
        context["shop"] = Shop.objects.get(user=self.request.user)
        return context


class CartItemDeleteView(APIView):
    """Удаление позиции из корзины."""

    permission_classes = (IsAuthenticated,)

    def delete(self, request, item_id):
        """Удалить позицию корзины (только свою)."""
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__user=request.user,
                order__status=Order.Status.BASKET,
            )
        except OrderItem.DoesNotExist:
            return Response(
                {"error": "Позиция не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartView(APIView):
    """Просмотр и добавление товаров в корзину текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Вернуть текущую корзину пользователя (создать пустую, если нет)."""
        order, _ = Order.objects.get_or_create(
            user=request.user,
            status=Order.Status.BASKET,
        )
        serializer = CartSerializer(order)
        return Response(serializer.data)

    def post(self, request):
        """Добавить позицию в корзину или увеличить её количество."""
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]
        shop_id = serializer.validated_data["shop_id"]
        quantity = serializer.validated_data["quantity"]

        try:
            product_info = ProductInfo.objects.get(
                product_id=product_id,
                shop_id=shop_id,
            )
        except ProductInfo.DoesNotExist:
            return Response(
                {"error": "Товар не найден в указанном магазине"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order, _ = Order.objects.get_or_create(
            user=request.user,
            status=Order.Status.BASKET,
        )

        item, created = OrderItem.objects.get_or_create(
            order=order,
            product_id=product_id,
            shop_id=shop_id,
            defaults={
                "quantity": quantity,
                "price": product_info.price,
            },
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(
            {"message": "Товар добавлен в корзину"},
            status=status.HTTP_201_CREATED,
        )
