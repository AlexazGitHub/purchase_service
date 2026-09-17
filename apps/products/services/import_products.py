"""Сервис импорта товаров из YAML-файлов поставщиков."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


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


def parse_yaml_file(file_path: str | Path) -> ImportData:
    """Прочитать и распарсить YAML-файл импорта товаров.

    :param file_path: путь к YAML-файлу.
    :return: структурированные данные импорта.
    :raises FileNotFoundError: если файл не найден.
    :raises yaml.YAMLError: если файл содержит некорректный YAML.
    :raises KeyError: если в файле отсутствуют обязательные поля.
    """
    with open(file_path, encoding="utf-8") as file:
        raw_data = yaml.safe_load(file)

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