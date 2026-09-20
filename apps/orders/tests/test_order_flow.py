"""Тест полного сценария создания заказа (happy path)."""

import pytest
from rest_framework.test import APIClient

from apps.orders.models import Order
from apps.products.models import Product, ProductInfo
from apps.shops.models import Category, Shop
from apps.users.models import Contact, User


@pytest.fixture
def api_client():
    """Клиент DRF для выполнения тестовых запросов."""
    return APIClient()


@pytest.mark.django_db
def test_full_order_flow(api_client):
    """Полный сценарий: добавление в корзину → подтверждение заказа."""
    buyer = User.objects.create_user(
        email="flow_buyer@example.com",
        password="SecurePass123!",
        is_active=True,
    )
    contact = Contact.objects.create(
        user=buyer,
        type="address",
        city="Москва",
        street="Тверская",
        house="1",
    )
    shop = Shop.objects.create(name="Связной")
    category = Category.objects.create(name="Смартфоны")
    product = Product.objects.create(name="iPhone", category=category)
    ProductInfo.objects.create(
        product=product,
        shop=shop,
        external_id=1,
        price=100000,
        price_rrc=110000,
        quantity=10,
    )

    api_client.force_authenticate(user=buyer)

    add_response = api_client.post(
        "/api/v1/orders/cart",
        {"product_id": product.id, "shop_id": shop.id, "quantity": 2},
    )
    assert add_response.status_code == 201

    confirm_response = api_client.post(
        "/api/v1/orders/confirm",
        {"contact_id": contact.id},
    )
    assert confirm_response.status_code == 200

    order = Order.objects.get(user=buyer)
    assert order.status == Order.Status.NEW
    assert order.contact_id == contact.id
    assert order.items.count() == 1
    assert order.items.first().quantity == 2
