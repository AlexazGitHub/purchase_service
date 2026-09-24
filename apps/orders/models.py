"""Модели заказов и их позиций."""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.products.models import Product
from apps.shops.models import Shop
from apps.users.models import Contact


class Order(TimeStampedModel):
    """Заказ пользователя."""

    class Status(models.TextChoices):
        """Статусы заказа."""

        BASKET = "basket", "В корзине"
        NEW = "new", "Новый"
        CONFIRMED = "confirmed", "Подтверждён"
        ASSEMBLED = "assembled", "Собран"
        SENT = "sent", "Отправлен"
        DELIVERED = "delivered", "Доставлен"
        CANCELED = "canceled", "Отменён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="orders",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=15,
        choices=Status.choices,
        default=Status.BASKET,
    )
    contact = models.ForeignKey(
        Contact,
        verbose_name="Контакт доставки",
        related_name="orders",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        """Строковое представление заказа."""
        return f"Заказ №{self.pk} ({self.get_status_display()})"


class OrderItem(TimeStampedModel):
    """Позиция заказа: товар из конкретного магазина."""

    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество",
        default=1,
    )
    price = models.DecimalField(
        verbose_name="Цена на момент заказа",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product", "shop"],
                name="unique_order_product_shop",
            )
        ]

    def __str__(self):
        """Строковое представление позиции заказа."""
        return f"{self.product.name} ({self.shop.name}) x{self.quantity}"
