"""Сервис импорта товаров из YAML-файлов поставщиков."""

from dataclasses import dataclass, field
from pathlib import Path
import yaml
from django.db import transaction

from apps.products.models import Parameter, Product, ProductInfo, ProductParameter
from apps.shops.models import Category, Shop


@dataclass
class GoodData:
    """Данные об одном товаре из YAML-файла."""

    external_id: int
    category_id: int
    model: str
    name: str
    price: float
    price_rrc: float
    quantity: int
    parameters: dict[str, str]


@dataclass
class ImportData:
    """Распарсенные данные импорта: магазин, категории, товары."""

    shop_name: str
    categories: dict[int, str] = field(default_factory=dict)
    goods: list[GoodData] = field(default_factory=list)


def parse_yaml_content(content: str) -> ImportData:
    """Распарсить YAML-содержимое (текст) в структуру импорта.

    :param content: содержимое YAML-файла в виде строки.
    :return: структурированные данные импорта.
    :raises yaml.YAMLError: если содержимое содержит некорректный YAML.
    :raises KeyError: если отсутствуют обязательные поля.
    """
    raw_data = yaml.safe_load(content)

    categories = {
        category["id"]: category["name"]
        for category in raw_data["categories"]
    }

    goods = [
        GoodData(
            external_id=item["id"],
            category_id=item["category"],
            model=item.get("model", ""),
            name=item["name"],
            price=item["price"],
            price_rrc=item["price_rrc"],
            quantity=item["quantity"],
            parameters={
                str(key): str(value)
                for key, value in item.get("parameters", {}).items()
            },
        )
        for item in raw_data["goods"]
    ]

    return ImportData(
        shop_name=raw_data["shop"],
        categories=categories,
        goods=goods,
    )


def parse_yaml_file(file_path: str | Path) -> ImportData:
    """Прочитать и распарсить YAML-файл импорта товаров.

    :param file_path: путь к YAML-файлу.
    :return: структурированные данные импорта.
    :raises FileNotFoundError: если файл не найден.
    :raises yaml.YAMLError: если файл содержит некорректный YAML.
    :raises KeyError: если в файле отсутствуют обязательные поля.
    """
    with open(file_path, encoding="utf-8") as file:
        content = file.read()
    return parse_yaml_content(content)


@transaction.atomic
def save_import_data(data: ImportData) -> Shop:
    """Сохранить распарсенные данные импорта в БД (upsert).

    Вся операция выполняется в одной транзакции: если что-то
    пойдёт не так на середине импорта, изменения полностью
    откатятся, БД не окажется в частично обновлённом состоянии.

    :param data: распарсенные данные импорта.
    :return: объект магазина, для которого выполнен импорт.
    """
    shop, _ = Shop.objects.get_or_create(name=data.shop_name)

    category_by_external_id = _save_categories(data.categories, shop)

    for good in data.goods:
        category = category_by_external_id[good.category_id]
        product = _save_product(good, category)
        _save_parameters(good, product)
        _save_product_info(good, product, shop)

    return shop


def _save_categories(
    categories: dict[int, str],
    shop: Shop,
) -> dict[int, Category]:
    """Создать/обновить категории и привязать их к магазину.

    :param categories: словарь {external_id: name} из YAML.
    :param shop: магазин, к которому привязываются категории.
    :return: словарь {external_id: объект Category} для
        дальнейшего сопоставления товаров с категориями.
    """
    result = {}
    for external_id, name in categories.items():
        category, _ = Category.objects.get_or_create(name=name)
        category.shops.add(shop)
        result[external_id] = category
    return result


def _save_product(good: GoodData, category: Category) -> Product:
    """Создать/найти товар по паре (название, категория).

    :param good: данные о товаре из YAML.
    :param category: категория товара.
    :return: объект товара.
    """
    product, _ = Product.objects.get_or_create(
        name=good.name,
        category=category,
    )
    return product


def _save_parameters(good: GoodData, product: Product) -> None:
    """Создать/обновить параметры товара.

    :param good: данные о товаре из YAML.
    :param product: товар, для которого сохраняются параметры.
    """
    for param_name, value in good.parameters.items():
        parameter, _ = Parameter.objects.get_or_create(name=param_name)
        ProductParameter.objects.update_or_create(
            product=product,
            parameter=parameter,
            defaults={"value": value},
        )


def _save_product_info(
    good: GoodData,
    product: Product,
    shop: Shop,
) -> None:
    """Создать/обновить информацию о товаре в магазине (цена, остаток).

    :param good: данные о товаре из YAML.
    :param product: товар.
    :param shop: магазин.
    """
    ProductInfo.objects.update_or_create(
        product=product,
        shop=shop,
        defaults={
            "external_id": good.external_id,
            "model": good.model,
            "quantity": good.quantity,
            "price": good.price,
            "price_rrc": good.price_rrc,
        },
    )