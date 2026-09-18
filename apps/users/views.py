"""API views приложения users."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from apps.users.models import EmailConfirmationToken, User
from apps.users.serializers import RegisterSerializer
from apps.users.serializers import LoginSerializer
from apps.users.serializers import ContactSerializer


class RegisterView(APIView):
    """Регистрация нового пользователя."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Создать неактивного пользователя, отправить письмо."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Регистрация успешна, подтвердите email"},
            status=status.HTTP_201_CREATED,
        )


class ConfirmRegistrationView(APIView):
    """Подтверждение email по токену."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Активировать пользователя по токену подтверждения."""
        email = request.data.get("email")
        token_key = request.data.get("token")

        if not email or not token_key:
            return Response(
                {"error": "Необходимо указать email и token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = EmailConfirmationToken.objects.get(
                user__email=email,
                key=token_key,
            )
        except EmailConfirmationToken.DoesNotExist:
            return Response(
                {"error": "Неверный email или токен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user
        user.is_active = True
        user.save()
        token.delete()

        return Response({"message": "Email подтверждён"})


class LoginView(APIView):
    """Вход пользователя, получение токена авторизации."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Проверить credentials, вернуть токен."""
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class ContactViewSet(ModelViewSet):
    """CRUD для контактов пользователя (только свои контакты)."""

    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Вернуть только контакты текущего пользователя."""
        return self.request.user.contacts.all()

    def perform_create(self, serializer):
        """Привязать создаваемый контакт к текущему пользователю."""
        serializer.save(user=self.request.user)
