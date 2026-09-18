"""Сериализаторы для приложения users."""

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя для отображения данных."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "company",
            "position",
            "type",
        )
        read_only_fields = ("id", "type")