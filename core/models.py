from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    title = models.CharField(_('title'), max_length=200, blank=True)
