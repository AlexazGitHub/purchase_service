"""Регистрация моделей products в админке."""

from django.contrib import admin

from apps.products.models import (
    Parameter,
    Product,
    ProductInfo,
    ProductParameter,
)

admin.site.register(Product)
admin.site.register(Parameter)
admin.site.register(ProductParameter)
admin.site.register(ProductInfo)
