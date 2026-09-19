"""API views приложения orders."""

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order
from apps.orders.serializers import OrderForPartnerSerializer
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
