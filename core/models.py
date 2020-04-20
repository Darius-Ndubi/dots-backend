from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    title = models.CharField(_('title'), max_length=200, blank=True)


class Workspace(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500)
    workspace_url = models.SlugField(unique=True)
