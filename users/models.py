from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser):
    """
    Кастомная модель пользователя.
    Поле username уникальное и используется для аутентификации
    Добавлено поле is_admin для идентификации админа
    """
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
    )
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    def __str__(self):
        return self.username
