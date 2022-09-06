from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import CreateCommonUserSerializer


class SignInView(CreateAPIView):
    """
    Создания простого пользователя
    """
    permission_classes = [AllowAny]
    serializer_class = CreateCommonUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
