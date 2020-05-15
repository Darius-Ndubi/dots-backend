from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from core.util.emails import send_welcome_email


@receiver(user_logged_in)
def update_last_login(sender, user, last_login=None, **kwargs):
    if not last_login:
        send_welcome_email(user)
