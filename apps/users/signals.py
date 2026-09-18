"""Сигналы приложения users."""

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

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