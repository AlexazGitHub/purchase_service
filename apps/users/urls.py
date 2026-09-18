"""URL-маршруты приложения users."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import (
    ConfirmRegistrationView,
    ContactViewSet,
    LoginView,
    RegisterView,
)

app_name = "users"

router = DefaultRouter()
router.register("contact", ContactViewSet, basename="contact")

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("register/confirm", ConfirmRegistrationView.as_view(), name="register-confirm"),
    path("login", LoginView.as_view(), name="login"),
    path("", include(router.urls)),
]
