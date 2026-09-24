"""Management-команда для импорта товаров из YAML-файла."""

import yaml
from django.core.management.base import BaseCommand, CommandError

from apps.products.services.import_products import (
    parse_yaml_file,
    save_import_data,
)


class Command(BaseCommand):
    """Команда импорта товаров поставщика из YAML-файла."""

    help = "Импортирует товары магазина из YAML-файла в базу данных"

    def add_arguments(self, parser):
        """Добавить аргумент командной строки — путь к файлу."""
        parser.add_argument(
            "file_path",
            type=str,
            help="Путь к YAML-файлу импорта товаров",
        )

    def handle(self, *args, **options):
        """Выполнить импорт товаров из указанного файла."""
        file_path = options["file_path"]

        try:
            data = parse_yaml_file(file_path)
        except FileNotFoundError as exc:
            raise CommandError(f"Файл не найден: {file_path}") from exc
        except yaml.YAMLError as exc:
            raise CommandError(
                f"Некорректный синтаксис YAML в файле {file_path}: {exc}"
            ) from exc
        except KeyError as exc:
            raise CommandError(
                f"В файле отсутствует обязательное поле: {exc}"
            ) from exc

        shop = save_import_data(data)

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершён: магазин «{shop.name}», "
                f"товаров обработано: {len(data.goods)}"
            )
        )
