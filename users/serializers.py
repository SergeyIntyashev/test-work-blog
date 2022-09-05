from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.settings import api_settings as settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя
    """
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('Invalid credentials, try again')

        if not user.check_password(password):
            raise AuthenticationFailed('Invalid credentials, try again')

        if not user.is_active:
            raise AuthenticationFailed('User is blocked, contact Admin')

        update_last_login(None, user)

        tokens = RefreshToken.for_user(user)

        return {
            'username': username,
            'is_admin': user.is_admin,
            'refresh': str(tokens),
            'access': str(tokens.access_token)
        }


class LogoutSerializer(serializers.Serializer):
    """
    Сериализатор для logout'а пользователя,
    токен заносится в black list
    """
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid',)
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


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
