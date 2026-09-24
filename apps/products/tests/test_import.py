"""Тесты импорта товаров из YAML."""

import pytest

from apps.products.models import Product, ProductInfo
from apps.products.services.import_products import (
    parse_yaml_file,
    save_import_data,
)
from apps.shops.models import Category, Shop


@pytest.mark.django_db
def test_import_creates_expected_objects():
    """Импорт shop1.yaml создаёт ожидаемое количество объектов."""
    data = parse_yaml_file("data/import_samples/shop1.yaml")
    shop = save_import_data(data)

    assert shop.name == "Связной"
    assert Shop.objects.count() == 1
    assert Category.objects.count() == 4
    assert Product.objects.count() == 14
    assert ProductInfo.objects.count() == 14


@pytest.mark.django_db
def test_repeated_import_does_not_create_duplicates():
    """Повторный импорт того же файла не создаёт дублей."""
    data = parse_yaml_file("data/import_samples/shop1.yaml")
    save_import_data(data)
    save_import_data(data)

    assert Shop.objects.count() == 1
    assert Product.objects.count() == 14
    assert ProductInfo.objects.count() == 14


@pytest.mark.django_db
def test_import_updates_existing_product_info():
    """Повторный импорт с изменённой ценой обновляет ProductInfo."""
    data = parse_yaml_file("data/import_samples/shop1.yaml")
    save_import_data(data)

    data.goods[0].price = 999999
    save_import_data(data)

    info = ProductInfo.objects.get(external_id=data.goods[0].external_id)
    assert info.price == 999999
