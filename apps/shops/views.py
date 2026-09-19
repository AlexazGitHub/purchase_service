"""API views приложения shops."""

import requests
import yaml
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.services.import_products import (
    parse_yaml_content,
    save_import_data,
)
from apps.users.permissions import IsShopUser


class PartnerUpdateView(APIView):
    """Импорт товаров магазина по URL на YAML-файл."""

    permission_classes = (IsAuthenticated, IsShopUser)

    def post(self, request):
        """Скачать и импортировать YAML-файл по переданному URL."""
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "Необходимо указать url"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            return Response(
                {"error": f"Не удалось загрузить файл: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = parse_yaml_content(response.text)
        except yaml.YAMLError as exc:
            return Response(
                {"error": f"Некорректный YAML: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError as exc:
            return Response(
                {"error": f"Отсутствует обязательное поле: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shop = save_import_data(data)

        return Response(
            {
                "message": f"Импорт завершён: магазин «{shop.name}», "
                f"товаров обработано: {len(data.goods)}"
            }
        )
