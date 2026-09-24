"""Регистрация моделей users в админке."""

from django.contrib import admin

from apps.users.models import Contact, User

admin.site.register(User)
admin.site.register(Contact)
