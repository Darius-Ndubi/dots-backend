from django.contrib.auth import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def update_last_login(sender, user, last_login, **kwargs):
    if not last_login:
        pass
