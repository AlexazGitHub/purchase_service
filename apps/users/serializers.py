"""Сериализаторы для приложения users."""

from rest_framework import serializers
from apps.users.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


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


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "company",
            "position",
        )

    def validate_password(self, value):
        """Проверить пароль стандартными валидаторами Django."""
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages))
        return value

    def create(self, validated_data):
        """Создать неактивного пользователя с хэшированным паролем."""
        password = validated_data.pop("password")
        user = User(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return user
