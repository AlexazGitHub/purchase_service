"""Сериализаторы для приложения users."""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate

from apps.users.models import Contact, User


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


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя (проверка credentials)."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Проверить email и пароль через стандартный authenticate()."""
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError(
                "Неверный email или пароль, либо email не подтверждён"
            )
        attrs["user"] = user
        return attrs


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор контакта пользователя (телефон/адрес)."""

    class Meta:
        model = Contact
        fields = (
            "id",
            "type",
            "phone",
            "city",
            "street",
            "house",
            "structure",
            "building",
            "apartment",
        )

    def validate(self, attrs):
        """Проверить бизнес-правила через Contact.clean()."""
        instance = Contact(
            user=self.context["request"].user,
            **{**{f: getattr(self.instance, f, "") for f in attrs}, **attrs}
            if self.instance
            else attrs,
        )
        if self.instance:
            instance.pk = self.instance.pk
        instance.clean()
        return attrs
