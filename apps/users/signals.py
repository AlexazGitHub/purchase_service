"""Сигналы приложения users."""

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created

from apps.users.models import EmailConfirmationToken, User


@receiver(post_save, sender=User)
def send_email_confirmation(sender, instance, created, **kwargs):
    """Отправить письмо с токеном подтверждения при регистрации.

    Срабатывает только при создании нового неактивного
    пользователя (то есть именно при регистрации, а не при
    любом сохранении пользователя, например, при подтверждении).
    """
    if not created or instance.is_active:
        return

    token = EmailConfirmationToken.objects.create(user=instance)

    send_mail(
        subject="Подтверждение регистрации",
        message=(
            f"Здравствуйте, {instance.email}!\n\n"
            f"Для подтверждения регистрации используйте токен:\n"
            f"{token.key}"
        ),
        from_email=None,
        recipient_list=[instance.email],
    )


@receiver(reset_password_token_created)
def send_password_reset_email(
    sender, instance, reset_password_token, **kwargs
):
    """Отправить письмо с токеном сброса пароля."""
    send_mail(
        subject="Восстановление пароля",
        message=(
            f"Здравствуйте, {reset_password_token.user.email}!\n\n"
            f"Для сброса пароля используйте токен:\n"
            f"{reset_password_token.key}"
        ),
        from_email=None,
        recipient_list=[reset_password_token.user.email],
    )
