from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from users.serializers import LoginSerializer, LogoutSerializer, \
    CreateCommonUserSerializer


class CreateCommonUser(GenericAPIView):
    """
    Создания простого пользователя
    """
    permission_classes = [AllowAny]
    serializer_class = CreateCommonUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(GenericAPIView):
    """
    Авторизация пользователя и получение JWT токена
    """
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(GenericAPIView):
    """
    Logout пользователя и занесение токена в black list
    """
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
