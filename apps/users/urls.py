"""URL-маршруты приложения users."""

from django.urls import path

from apps.users.views import ConfirmRegistrationView, LoginView, RegisterView

app_name = "users"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("register/confirm", ConfirmRegistrationView.as_view(), name="register-confirm"),
    path("login", LoginView.as_view(), name="login"),
]
