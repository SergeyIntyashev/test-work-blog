from django.utils import timezone
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blogs.models import Blogs
from blogs import serializers
from blogs.services import user_can_publish_post, check_and_get_post, \
    add_like_to_post
from config.permissions import IsAuthenticatedAndOwner, IsAdminUser


class CreateBlog(generics.CreateAPIView):
    """
    Создание блога
    """

    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.CreateBlogSerializer

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class AddAuthorsToBlogView(generics.UpdateAPIView):
    """
    Добавление авторов в блог, где пользователь является owner'ом
    """

    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]
    serializer_class = serializers.AddAuthorsToBlogSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Blogs.objects.filter(owner=self.request.user)


class PublishPostView(generics.CreateAPIView):
    """
    Публикация поста в блог
    """

    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.PublishPostSerializer
    lookup_field = 'blog_id'

    def perform_create(self, serializer):

        if not user_can_publish_post(blog_id=self.kwargs['blog_id'],
                                     user=self.request.user):
            self.permission_denied(
                self.request,
                message="You can't publish posts on this blog,"
                        "because you are not an author or a blog owner",
                code=status.HTTP_403_FORBIDDEN
            )

        serializer.validated_data['author'] = self.request.user

        if serializer.validated_data['is_published']:
            serializer.validated_data['created_at'] = timezone.now()

        serializer.save()


class CreateCommentView(generics.CreateAPIView):
    """
    Создание комментария для поста
    """
    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.CreateCommentSerializer

    def perform_create(self, serializer):
        post = check_and_get_post(post_id=self.kwargs['post_id'],
                                  blog_id=self.kwargs['blog_id'],
                                  request=self.request)

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
                                  blog_id=kwargs['blog_id'],
                                  request=request)
        add_like_to_post(post)

        return Response(status=status.HTTP_200_OK)


class ListBlogView(generics.ListAPIView):
    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [IsAuthenticated | IsAdminUser]
