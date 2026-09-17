"""Регистрация моделей shops в админке."""

from django.contrib import admin

from apps.shops.models import Category, Shop

admin.site.register(Shop)
admin.site.register(Category)
