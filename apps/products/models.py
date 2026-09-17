"""Модели товаров и их характеристик (EAV)."""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.shops.models import Category


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