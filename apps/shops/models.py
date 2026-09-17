"""Модели магазинов и категорий товаров."""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Shop(TimeStampedModel):
    """Магазин-поставщик товаров."""

    name = models.CharField(
        verbose_name="Название",
        max_length=100,
        unique=True,
    )
    url = models.URLField(
        verbose_name="Ссылка на файл импорта товаров",
        blank=True,
        null=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        related_name="shop",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    state = models.BooleanField(
        verbose_name="Принимает заказы",
        default=True,
    )

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        """Строковое представление магазина."""
        return self.name


class Category(TimeStampedModel):
    """Категория товаров. Вложенность категорий не предусмотрена."""

    name = models.CharField(
        verbose_name="Название",
        max_length=100,
        unique=True,
    )
    shops = models.ManyToManyField(
        Shop,
        verbose_name="Магазины",
        related_name="categories",
        blank=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        """Строковое представление категории."""
        return self.name