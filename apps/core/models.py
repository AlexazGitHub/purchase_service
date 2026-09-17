"""Абстрактные базовые модели, переиспользуемые в других приложениях."""

from django.db import models


class TimeStampedModel(models.Model):
    """Абстрактная модель с временными метками создания и изменения.

    Наследники получают поля created_at и updated_at автоматически,
    без необходимости дублировать их в каждой модели.
    """

    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        verbose_name="Дата изменения",
        auto_now=True,
    )

    class Meta:
        abstract = True
