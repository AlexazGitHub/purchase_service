"""API views приложения shops."""

import requests
import yaml
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.services.import_products import (
    parse_yaml_content,
    save_import_data,
)
from apps.shops.models import Category, Shop
from apps.shops.serializers import CategorySerializer, ShopSerializer
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
        if shop.user_id is None:
            shop.user = request.user
            shop.save()

        return Response(
            {
                "message": f"Импорт завершён: магазин «{shop.name}», "
                f"товаров обработано: {len(data.goods)}"
            }
        )


class PartnerStateView(APIView):
    """Получение и изменение статуса приёма заказов магазином."""

    permission_classes = (IsAuthenticated, IsShopUser)

    def get(self, request):
        """Вернуть текущий статус приёма заказов."""
        shop = self._get_shop(request.user)
        return Response({"state": shop.state})

    def post(self, request):
        """Изменить статус приёма заказов."""
        shop = self._get_shop(request.user)
        state = request.data.get("state")

        if not isinstance(state, bool):
            return Response(
                {"error": "Поле state должно быть true или false"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shop.state = state
        shop.save()
        return Response({"state": shop.state})

    def _get_shop(self, user):
        """Получить магазин, привязанный к пользователю."""
        return Shop.objects.get(user=user)


class ShopListView(ListAPIView):
    """Список магазинов, принимающих заказы."""

    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = (AllowAny,)


class CategoryListView(ListAPIView):
    """Список категорий товаров."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)
