from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from blogs import serializers, services
from blogs.models import Blogs, Posts, Comments, Tags
from users.permissions import IsAuthenticatedAndOwner, IsAdminUser, \
    IsAuthorOrBlogOwner, IsAdminOrReadOnly


class BlogsView(ModelViewSet):
    """
    View для блогов
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filter_fields = ['created_at']
    search_fields = ['@title', '@authors__username']
    ordering_fields = ['title', 'created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]

        return [permission() for permission in permission_classes]

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
        return Blogs.objects.prefetch_related('authors').filter(
            owner=self.request.user.id)


class SubscribeToBlogView(generics.UpdateAPIView):
    """
    Подписка пользователя на блог
    """
    queryset = Blogs.objects.prefetch_related('subscriptions').all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddSubscriptionsToBlogSerializer
    http_method_names = ["patch"]


class ListFavoriteBlogsView(generics.ListAPIView):
    """
    Блоги на которые подписан пользователь
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BlogSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filter_fields = ['created_at']
    search_fields = ['@title', '@authors__username']
    ordering_fields = ['title', 'created_at']

    def get_queryset(self):
        return Blogs.objects.prefetch_related('subscriptions').filter(
            subscriptions__id=self.request.user.id)


class ListUserPostsView(generics.ListAPIView):
    """
    Посты опубликованные пользователем
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = services.PostFilter
    search_fields = ['@title', '@author__username']
    ordering_fields = ['title', 'created_at', 'likes']

    def get_queryset(self):
        return Posts.objects.filter(author=self.request.user.id)


class ListPostsOfBlogView(generics.ListAPIView):
    """
    Список постов блога
    """

    permission_classes = [AllowAny]
    serializer_class = serializers.PostSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = services.PostFilter
    search_fields = ['@title', '@author__username']
    ordering_fields = ['title', 'created_at', 'likes']

    def get_queryset(self):
        queryset = Posts.objects.none()
        if not getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            queryset = Posts.objects.filter(
                is_published=True,
                blog=self.kwargs['pk']
            )

        return queryset


class PostsView(ModelViewSet):
    """
    View для постов
    """

    serializer_class = serializers.PostSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )
    filterset_class = services.PostFilter
    search_fields = ['@title', '@author__username']
    ordering_fields = ['title', 'created_at', 'likes']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [
                IsAuthenticated,
                IsAuthorOrBlogOwner | IsAdminUser
            ]
        else:
            permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Posts.objects.all()
        if self.action == 'list':
            queryset = Posts.objects.filter(is_published=True)
        elif self.action == 'retrieve':
            queryset = Posts.objects.select_related('blog').all()

        return queryset

    def perform_create(self, serializer):
        blog = get_object_or_404(Blogs.objects.all(), id=self.kwargs['blog'])
        self.check_object_permissions(self.request, blog)

        serializer.validated_data['blog'] = blog
        serializer.validated_data['author'] = self.request.user

        if serializer.validated_data['is_published']:
            serializer.validated_data['created_at'] = timezone.now()

        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """
        Автоувеличение количества просмотров
        Не разрешаем владельцу блога набивать просмотры
        """

        services.increase_views_of_post(post=self.get_object(),
                                        user=self.request.user)
        return super().retrieve(request, *args, **kwargs)


class LikePostView(generics.GenericAPIView):
    """
    Увеличение лайка у поста
    """

    queryset = Posts.objects.all()
    permission_classes = [IsAuthenticated | IsAdminUser]

    def patch(self):
        post = self.get_object()
        services.increase_likes_of_post(post)

        return Response(status=status.HTTP_200_OK)


class CreateCommentView(generics.CreateAPIView):
    """
    Создание комментария для поста
    """

    queryset = Posts.objects.all()
    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.CommentSerializer

    def perform_create(self, serializer):
        post = self.get_object()

        serializer.validated_data['author'] = self.request.user
        serializer.validated_data['post'] = post

        serializer.save()


class CommentView(ModelViewSet):
    """
    View для комментариев
    CRUD для администратора
    Read-only для всех
    """
    queryset = Comments.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.CommentSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('post',)

    def perform_create(self, serializer):
        serializer.validated_data['author'] = self.request.user
        serializer.save()


class TagsView(ModelViewSet):
    """
    View для тэгов
    CRUD для администратора
    Read-only для всех
    """
    queryset = Tags.objects.order_by('title').all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.TagSerializer
