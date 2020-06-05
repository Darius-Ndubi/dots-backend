from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    title = models.CharField(_('title'), max_length=200, blank=True)
    history = HistoricalRecords()


class UserActivation(models.Model):
    user = models.ForeignKey(User, related_name='activation', on_delete=models.CASCADE)
    key = models.CharField(max_length=100)


class Workspace(models.Model):
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(blank=True)
    location = models.TextField(blank=True)
    url = models.URLField(max_length=500, blank=True)
    slug = models.SlugField(unique=True)
    history = HistoricalRecords()

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
    user = models.ForeignKey(User, related_name='membership', on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, related_name='membership', on_delete=models.CASCADE)
    role = models.CharField(max_length=6, default=MEMBER, choices=ROLE_CHOICES)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('user', 'workspace',)


class WorkspaceInvitation(models.Model):
    workspace = models.ForeignKey(Workspace, related_name='invites', on_delete=models.CASCADE)
    email = models.EmailField(_('email address'))
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    key = models.CharField(max_length=100)

    class Meta:
        unique_together = ['workspace', 'email']
