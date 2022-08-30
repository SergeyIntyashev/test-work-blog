from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from blogs.models import Blogs
from blogs.serializers import BlogSerializer, AddAuthorsToBlogSerializer
from config.permissions import IsAuthenticatedAndOwner, IsAdminUser


class CreateBlog(CreateAPIView):
    """
    Создание блога
    """

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = BlogSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class AddAuthorsToBlog(UpdateAPIView):
    """
    Добавление авторов в блог, где пользователь является owner'ом
    """

    permission_classes = [IsAuthenticatedAndOwner, IsAdminUser]
    serializer_class = AddAuthorsToBlogSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Blogs.objects.filter(owner=self.request.user)
