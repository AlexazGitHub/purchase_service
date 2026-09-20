"""Тесты регистрации, подтверждения email и авторизации."""

import pytest
from rest_framework.test import APIClient

from apps.users.models import EmailConfirmationToken, User


@pytest.fixture
def api_client():
    """Клиент DRF для выполнения тестовых запросов."""
    return APIClient()


@pytest.mark.django_db
def test_registration_creates_inactive_user(api_client):
    """Регистрация создаёт пользователя с is_active=False."""
    response = api_client.post(
        "/api/v1/user/register",
        {
            "email": "reg_test@example.com",
            "password": "SecurePass123!",
            "first_name": "Иван",
            "last_name": "Иванов",
        },
    )

    assert response.status_code == 201
    user = User.objects.get(email="reg_test@example.com")
    assert user.is_active is False


@pytest.mark.django_db
def test_confirmation_activates_user(api_client):
    """Подтверждение токеном активирует пользователя."""
    user = User.objects.create_user(
        email="confirm_test@example.com",
        password="SecurePass123!",
        is_active=False,
    )
    token = EmailConfirmationToken.objects.get(user=user)

    response = api_client.post(
        "/api/v1/user/register/confirm",
        {"email": user.email, "token": token.key},
    )

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_login_fails_for_unconfirmed_user(api_client):
    """Вход неподтверждённого пользователя отклоняется."""
    User.objects.create_user(
        email="unconfirmed@example.com",
        password="SecurePass123!",
        is_active=False,
    )

    response = api_client.post(
        "/api/v1/user/login",
        {"email": "unconfirmed@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_succeeds_after_confirmation(api_client):
    """Вход работает после активации пользователя."""
    User.objects.create_user(
        email="active_test@example.com",
        password="SecurePass123!",
        is_active=True,
    )

    response = api_client.post(
        "/api/v1/user/login",
        {"email": "active_test@example.com", "password": "SecurePass123!"},
    )

    assert response.status_code == 200
    assert "token" in response.data
