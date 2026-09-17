"""Модели товаров и их характеристик (EAV)."""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.shops.models import Category, Shop


class Product(TimeStampedModel):
    """Товар. Общие характеристики не зависят от магазина."""

    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        """Строковое представление товара."""
        return self.name


class Parameter(TimeStampedModel):
    """Справочник возможных характеристик товаров."""

    name = models.CharField(
        verbose_name="Название параметра",
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = "Параметр"
        verbose_name_plural = "Параметры"

    def __str__(self):
        """Строковое представление параметра."""
        return self.name


class ProductParameter(TimeStampedModel):
    """Значение конкретного параметра у конкретного товара."""

    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        related_name="parameters",
        on_delete=models.CASCADE,
    )
    parameter = models.ForeignKey(
        Parameter,
        verbose_name="Параметр",
        related_name="product_parameters",
        on_delete=models.CASCADE,
    )
    value = models.CharField(
        verbose_name="Значение",
        max_length=200,
    )

    class Meta:
        verbose_name = "Параметр товара"
        verbose_name_plural = "Параметры товаров"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "parameter"],
                name="unique_product_parameter",
            )
        ]

    def __str__(self):
        """Строковое представление параметра товара."""
        return f"{self.product.name} — {self.parameter.name}: {self.value}"


class ProductInfo(TimeStampedModel):
    """Информация о товаре в конкретном магазине: цена, остаток."""

    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    shop = models.ForeignKey(
        Shop,
        verbose_name="Магазин",
        related_name="product_infos",
        on_delete=models.CASCADE,
    )
    external_id = models.PositiveIntegerField(
        verbose_name="Внешний ID товара у поставщика",
    )
    model = models.CharField(
        verbose_name="Артикул",
        max_length=100,
        blank=True,
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество на складе",
        default=0,
    )
    price = models.DecimalField(
        verbose_name="Цена",
        max_digits=10,
        decimal_places=2,
    )
    price_rrc = models.DecimalField(
        verbose_name="Рекомендованная розничная цена",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Информация о товаре"
        verbose_name_plural = "Информация о товарах"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "shop"],
                name="unique_product_shop",
            )
        ]

    def __str__(self):
        """Строковое представление записи о товаре в магазине."""
        return f"{self.product.name} в {self.shop.name}: {self.price}"