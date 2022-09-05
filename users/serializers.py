from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.settings import api_settings as settings

from users.models import CustomUser


class CreateCommonUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя
    """
    password = serializers.CharField(style={'input_type': 'password'},
                                     write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password')

    def validate(self, attrs):
        """
        Валидация для регистрации простых пользователей
        """
        user = CustomUser(**attrs)
        password = attrs.get('password')
        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {
                    "password": serializer_error[settings.NON_FIELD_ERRORS_KEY]
                }
            )
        return attrs

    def create(self, validated_data):
        try:
            user = self._perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        return user

    def _perform_create(self, validated_data):
        with transaction.atomic():
            user = CustomUser.objects.create_common_user(**validated_data)
        return user
