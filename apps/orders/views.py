"""API views приложения orders."""

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Contact, Order, OrderItem
from apps.orders.serializers import (
    AddToCartSerializer,
    CartSerializer,
    ConfirmOrderSerializer,
    OrderForPartnerSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)
from apps.products.models import ProductInfo
from apps.shops.models import Shop
from apps.users.permissions import IsShopUser


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

        existing_item = OrderItem.objects.filter(
            order__user=request.user,
            order__status=Order.Status.BASKET,
            product_id=product_id,
            shop_id=shop_id,
        ).first()
        already_in_cart = existing_item.quantity if existing_item else 0

        if already_in_cart + quantity > product_info.quantity:
            return Response(
                {
                    "error": f"Недостаточно товара на складе. "
                    f"Доступно: {product_info.quantity}, "
                    f"в корзине уже: {already_in_cart}"
                },
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


class ConfirmOrderView(APIView):
    """Подтверждение заказа: выбор контакта, смена статуса."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Подтвердить текущую корзину как заказ."""
        serializer = ConfirmOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_id = serializer.validated_data["contact_id"]

        try:
            order = Order.objects.get(
                user=request.user,
                status=Order.Status.BASKET,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not order.items.exists():
            return Response(
                {"error": "Корзина пуста"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            contact = Contact.objects.get(
                id=contact_id,
                user=request.user,
                type=Contact.ContactType.ADDRESS,
            )
        except Contact.DoesNotExist:
            return Response(
                {"error": "Контакт не найден или не принадлежит вам"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.contact = contact
        order.status = Order.Status.NEW
        order.save()

        self._send_notifications(order)

        return Response({"message": f"Заказ №{order.id} оформлен"})

    def _send_notifications(self, order):
        """Отправить письма о подтверждении заказа покупателю и админу."""
        items_text = "\n".join(
            f"- {item.product.name} ({item.shop.name}) x{item.quantity}"
            for item in order.items.all()
        )
        message = (
            f"Заказ №{order.id} оформлен.\n\n" f"Состав заказа:\n{items_text}"
        )

        send_mail(
            subject=f"Ваш заказ №{order.id} оформлен",
            message=message,
            from_email=None,
            recipient_list=[order.user.email],
        )

        if settings.ADMIN_EMAIL:
            send_mail(
                subject=f"Новый заказ №{order.id}",
                message=message,
                from_email=None,
                recipient_list=[settings.ADMIN_EMAIL],
            )


class OrderListView(ListAPIView):
    """Список оформленных заказов текущего пользователя."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Вернуть только оформленные заказы текущего пользователя."""
        return Order.objects.filter(
            user=self.request.user,
        ).exclude(status=Order.Status.BASKET)


class OrderDetailView(RetrieveAPIView):
    """Детали конкретного заказа текущего пользователя."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Вернуть только заказы текущего пользователя (не чужие)."""
        return Order.objects.filter(
            user=self.request.user,
        ).exclude(status=Order.Status.BASKET)


class OrderStatusUpdateView(APIView):
    """Смена статуса заказа администратором."""

    permission_classes = (IsAdminUser,)

    def patch(self, request, pk):
        """Изменить статус указанного заказа."""
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Заказ не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data["status"]
        order.save()

        return Response({"message": f"Статус заказа №{order.id} изменён"})
