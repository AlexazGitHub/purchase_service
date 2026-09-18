"""Модели пользователей сервиса покупок."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError

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
    last_name = models.CharField(
        verbose_name="Фамилия",
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


class Contact(TimeStampedModel):
    """Контакт пользователя: телефон или адрес доставки.

    У пользователя может быть не более одного телефона
    и не более пяти адресов (проверяется в clean()).
    """

    class ContactType(models.TextChoices):
        """Тип контакта."""

        PHONE = "phone", "Телефон"
        ADDRESS = "address", "Адрес"

    MAX_ADDRESSES_PER_USER = 5

    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="contacts",
        on_delete=models.CASCADE,
    )
    type = models.CharField(
        verbose_name="Тип контакта",
        max_length=10,
        choices=ContactType.choices,
    )
    phone = models.CharField(
        verbose_name="Телефон",
        max_length=20,
        blank=True,
    )
    city = models.CharField(
        verbose_name="Город",
        max_length=50,
        blank=True,
    )
    street = models.CharField(
        verbose_name="Улица",
        max_length=100,
        blank=True,
    )
    house = models.CharField(
        verbose_name="Дом",
        max_length=15,
        blank=True,
    )
    structure = models.CharField(
        verbose_name="Корпус",
        max_length=15,
        blank=True,
    )
    building = models.CharField(
        verbose_name="Строение",
        max_length=15,
        blank=True,
    )
    apartment = models.CharField(
        verbose_name="Квартира",
        max_length=15,
        blank=True,
    )

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        """Строковое представление контакта."""
        if self.type == self.ContactType.PHONE:
            return f"{self.user.email}: тел. {self.phone}"
        return f"{self.user.email}: {self.city}, {self.street}"

    def clean(self):
        """Валидация бизнес-правил: 1 телефон, до 5 адресов."""
        super().clean()

        if self.type == self.ContactType.PHONE:
            self._validate_single_phone()
        elif self.type == self.ContactType.ADDRESS:
            self._validate_max_addresses()

    def _validate_single_phone(self):
        """Проверить, что у пользователя ещё нет телефона."""
        existing = Contact.objects.filter(
            user=self.user,
            type=self.ContactType.PHONE,
        ).exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError(
                "У пользователя уже есть телефонный контакт"
            )

    def _validate_max_addresses(self):
        """Проверить, что у пользователя не более 5 адресов."""
        existing_count = Contact.objects.filter(
            user=self.user,
            type=self.ContactType.ADDRESS,
        ).exclude(pk=self.pk).count()
        if existing_count >= self.MAX_ADDRESSES_PER_USER:
            raise ValidationError(
                f"Нельзя добавить более "
                f"{self.MAX_ADDRESSES_PER_USER} адресов"
            )