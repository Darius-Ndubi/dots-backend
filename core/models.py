from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    title = models.CharField(_('title'), max_length=200, blank=True)


class Workspace(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(blank=True)
    location = models.TextField(blank=True)
    url = models.URLField(max_length=500, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ADMIN = 'ADMIN'
    OWNER = 'OWNER'
    MEMBER = 'MEMBER'

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (OWNER, 'Owner'),
        (MEMBER, 'Member'),
    )
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name="membership", on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, related_name="membership", on_delete=models.CASCADE)
    role = models.CharField(max_length=6, default=MEMBER, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'workspace',)
