from django.contrib.auth import user_logged_in
from django.dispatch import receiver

from core.util.emails import send_welcome_email


@receiver(user_logged_in)
def update_last_login(sender, user, is_new=False, **kwargs):
    if is_new:
        send_welcome_email(user)
