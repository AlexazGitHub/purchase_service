"""URL-маршруты приложения users."""

from django.urls import path

from apps.users.views import ConfirmRegistrationView, RegisterView

app_name = "users"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("register/confirm", ConfirmRegistrationView.as_view(), name="register-confirm"),
]
