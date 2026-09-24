# Purchase Service

Дипломный проект: backend-сервис для автоматизации закупок товаров у нескольких поставщиков (магазинов).

## Стек
- Python 3.14, Django 5.2 (LTS), Django REST Framework
- PostgreSQL 14
- pytest, pytest-django

## Установка и запуск

```bash
git clone git@github.com:AlexazGitHub/purchase_service.git
cd purchase_service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # заполнить реальными значениями (пароль БД, SECRET_KEY, ADMIN_EMAIL)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Тесты:
```bash
pytest
```

## Роли пользователей
- **Покупатель (buyer)** — регистрируется самостоятельно через `POST /api/v1/user/register`.
- **Магазин (shop)** — создаётся администратором вручную (через админку или `manage.py shell`), публичной регистрации магазина нет — это осознанное архитектурное решение (партнёрство подключается не самостоятельной регистрацией).

## Основные эндпоинты
- `POST /api/v1/user/register`, `/register/confirm`, `/login` — регистрация, подтверждение email, вход
- `POST /api/v1/password_reset/`, `/password_reset/confirm/` — восстановление пароля
- `GET/POST/DELETE /api/v1/user/contact/` — контакты пользователя (телефон/адрес)
- `POST /api/v1/shops/partner/update` — импорт товаров по URL (только для типа shop)
- `GET/POST /api/v1/shops/partner/state` — статус приёма заказов магазином
- `GET /api/v1/orders/partner/orders` — заказы, содержащие товары магазина
- `GET /api/v1/products/`, `/{id}` — каталог товаров (фильтры `shop_id`, `category_id`)
- `GET /api/v1/shops/`, `/categories` — справочники
- `GET/POST /api/v1/orders/cart`, `DELETE /cart/{id}` — корзина
- `POST /api/v1/orders/confirm` — подтверждение заказа
- `GET /api/v1/orders/`, `/{id}` — список и детали заказов пользователя
- `PATCH /api/v1/orders/{id}/status` — смена статуса заказа (только для is_staff)

## Импорт товаров из shell (без API)
```bash
python manage.py import_products data/import_samples/shop1.yaml
```

## Статус
Базовая (обязательная) часть ТЗ реализована.
