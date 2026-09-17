"""Модели пользователей сервиса покупок."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    """Менеджер модели User с логином по email вместо username."""

    def create_user(self, email, password=None, **extra_fields):
        """Создать и сохранить обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен для создания пользователя")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создать и сохранить суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Суперпользователь должен иметь is_superuser=True"
            )

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Пользователь сервиса: покупатель или представитель магазина."""

    class UserType(models.TextChoices):
        """Тип пользователя."""

        BUYER = "buyer", "Покупатель"
        SHOP = "shop", "Магазин"

    email = models.EmailField(
        verbose_name="Email",
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=100,
        blank=True,
    )
    company = models.CharField(
        verbose_name="Компания",
        max_length=150,
        blank=True,
    )
    position = models.CharField(
        verbose_name="Должность",
        max_length=150,
        blank=True,
    )
    type = models.CharField(
        verbose_name="Тип пользователя",
        max_length=10,
        choices=UserType.choices,
        default=UserType.BUYER,
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True,
    )
    is_staff = models.BooleanField(
        verbose_name="Доступ в админку",
        default=False,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Строковое представление пользователя."""
        return self.email