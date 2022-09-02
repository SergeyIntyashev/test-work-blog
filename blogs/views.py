from django.utils import timezone
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from blogs import serializers
from blogs.models import Blogs
from blogs.services import check_and_get_post, \
    add_like_to_post
from config.permissions import IsAuthenticatedAndOwner, IsAdminUser, \
    IsAuthorOrBlogOwner


# BLOG VIEWS
class ListBlogView(generics.ListAPIView):
    """
    Список блогов
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [AllowAny]


class CreateBlogView(generics.CreateAPIView):
    """
    Создание блога
    """

    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.BlogSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class RetrieveBlogView(generics.RetrieveAPIView):
    """
    Получение блога
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [AllowAny]


class UpdateBlogView(generics.UpdateAPIView):
    """
    Обновление блога
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]


class DestroyBlogView(generics.DestroyAPIView):
    """
    Удаление блога
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]


class AddAuthorsToBlogView(generics.UpdateAPIView):
    """
    Добавление авторов в блог, где пользователь является owner'ом
    """

    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]
    serializer_class = serializers.AddAuthorsToBlogSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Blogs.objects.prefetch_related('authors').filter(
            owner=self.request.user)


# POST VIEWS

class PublishPostView(generics.CreateAPIView):
    """
    Публикация поста в блог
    """

    permission_classes = [IsAuthenticated, IsAuthorOrBlogOwner | IsAdminUser]
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return not Blogs.objects.filter(id=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        blog = self.get_object()

        serializer.validated_data['blog'] = blog
        serializer.validated_data['author'] = self.request.user

        if serializer.validated_data['is_published']:
            serializer.validated_data['created_at'] = timezone.now()

        serializer.save()


class CreateCommentView(generics.CreateAPIView):
    """
    Создание комментария для поста
    """

    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.CommentSerializer

    def perform_create(self, serializer):
        post = check_and_get_post(post_id=self.kwargs['post_id'],
                                  blog_id=self.kwargs['blog_id'])

        serializer.validated_data['author'] = self.request.user
        serializer.validated_data['post'] = post

        serializer.save()


class LikePostView(APIView):
    """
    Увеличение лайка у поста
    """

    permission_classes = [IsAuthenticated | IsAdminUser]

    def patch(self, request, *args, **kwargs):
        post = check_and_get_post(post_id=kwargs['post_id'],
                                  blog_id=kwargs['blog_id'])
        add_like_to_post(post)

        return Response(status=status.HTTP_200_OK)
