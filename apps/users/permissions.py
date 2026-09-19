"""Кастомные права доступа приложения users."""

from rest_framework.permissions import BasePermission

from apps.users.models import User


class IsShopUser(BasePermission):
    """Доступ только для авторизованных пользователей типа «магазин»."""

    message = "Доступ разрешён только пользователям с типом «магазин»"

    def has_permission(self, request, view):
        """Проверить, что пользователь авторизован и имеет тип shop."""
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.type == User.UserType.SHOP
        )
