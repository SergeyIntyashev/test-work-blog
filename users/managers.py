from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User, где уникальное поле username
    используется для аутентификации
    """

    def _create_user(self, username, password, **extra_fields):
        """
        Создает и сохраняет пользователя с именем пользователя и паролем
        """
        if not username:
            raise ValueError(_('Поле username должно быть заполнено'))
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_common_user(self, username, password, **extra_fields):
        """
        Создает и сохраняет обычного пользователя
        """
        extra_fields.setdefault('is_admin', False)

        return self._create_user(
            username=username,
            password=password,
            **extra_fields
        )

    def create_superuser(self, username, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя-админа
        """
        extra_fields.setdefault('is_admin', True)

        assert extra_fields['is_admin']

        return self._create_user(
            username=username,
            password=password,
            **extra_fields
        )
