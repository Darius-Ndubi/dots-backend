from django.dispatch import receiver
from .signals import *


@receiver(user_logged_in)
def update_last_login(sender, user, **kwargs):
    if not user.last_login:
        pass
