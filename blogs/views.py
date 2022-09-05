from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from blogs import serializers, services
from blogs.models import Blogs, Posts, Comments, Tags
from config.permissions import IsAuthenticatedAndOwner, IsAdminUser, \
    IsAuthorOrBlogOwner, IsAdminOrReadOnly


# BLOG VIEWS
class ListBlogView(generics.ListAPIView):
    """
    Список блогов
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['created_at']


class CreateBlogView(generics.CreateAPIView):
    """
    Создание блога
    """

    permission_classes = [IsAuthenticated]
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


class UpdateDestroyBlogView(generics.RetrieveUpdateDestroyAPIView):
    """
    Обновление, удаление блога
    """

    queryset = Blogs.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]
    http_method_names = ('put', 'patch', 'delete')


class AddAuthorsToBlogView(generics.UpdateAPIView):
    """
    Добавление авторов в блог, где пользователь является owner'ом
    """

    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]
    serializer_class = serializers.AddAuthorsToBlogSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Blogs.objects.prefetch_related('authors').filter(
            id=self.kwargs[self.lookup_field])


class SubscribeToBlogView(generics.UpdateAPIView):
    """
    Подписка пользователя на блог
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AddSubscriptionsToBlogSerializer
    http_method_names = ["patch"]

    def get_queryset(self):
        return Blogs.objects.prefetch_related('subscriptions').filter(
            id=self.kwargs[self.lookup_field])


class ListFavoriteBlogsView(generics.ListAPIView):
    """
    Блоги на которые подписан пользователь
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BlogSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ['created_at']

    def get_queryset(self):
        return Blogs.objects.prefetch_related('subscriptions').filter(
            subscriptions__user=self.request.user.id)


# POST VIEWS
class ListUserPostsView(generics.ListAPIView):
    """
    Посты опубликованные пользователем
    """
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = services.PostFilter

    def get_queryset(self):
        return Posts.objects.filter(author=self.request.user)


class ListPostsView(generics.ListAPIView):
    """
    Список постов со всех блогов
    """

    queryset = Posts.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    serializer_class = serializers.PostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = services.PostFilter


class ListPostsOfBlogView(generics.ListAPIView):
    """
    Список постов блога
    """

    permission_classes = [AllowAny]
    serializer_class = serializers.PostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = services.PostFilter

    def get_queryset(self):
        return Posts.objects.filter(blog=self.kwargs[self.lookup_field])


class CreatePostView(generics.CreateAPIView):
    """
    Создание поста
    """

    permission_classes = [IsAuthenticated, IsAuthorOrBlogOwner | IsAdminUser]
    serializer_class = serializers.PostSerializer

    def get_queryset(self):
        return Blogs.objects.filter(id=self.kwargs[self.lookup_field])

    def perform_create(self, serializer):
        blog = self.get_object()

        serializer.validated_data['blog'] = blog
        serializer.validated_data['author'] = self.request.user

        if serializer.validated_data['is_published']:
            serializer.validated_data['created_at'] = timezone.now()

        serializer.save()


class RetrievePostView(generics.RetrieveAPIView):
    """
    Получение поста
    """

    queryset = Posts.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Posts.objects.select_related('blog').filter(
            id=self.kwargs[self.lookup_field])

    def get(self, request, *args, **kwargs):
        """
        Автоувеличение количества просмотров
        Не разрешаем владельцу блога набивать просмотры
        """

        services.increase_views_of_post(post=self.get_object(),
                                        user=self.request.user)
        return super().get(request, *args, **kwargs)


class UpdateDestroyPostView(generics.RetrieveUpdateDestroyAPIView):
    """
    Обновление, удаление поста
    """

    queryset = Posts.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [IsAuthenticatedAndOwner | IsAdminUser]
    http_method_names = ('put', 'patch', 'delete')


class LikePostView(APIView):
    """
    Увеличение лайка у поста
    """

    permission_classes = [IsAuthenticated | IsAdminUser]

    def post(self, request, *args, **kwargs):
        post = generics.get_object_or_404(Posts,
                                          id=self.kwargs['pk'])
        services.increase_likes_of_post(post)

        return Response(status=status.HTTP_200_OK)


class CreateCommentView(generics.CreateAPIView):
    """
    Создание комментария для поста
    """

    permission_classes = [IsAuthenticated | IsAdminUser]
    serializer_class = serializers.CommentSerializer

    def get_queryset(self):
        return Posts.objects.filter(id=self.kwargs[self.lookup_field])

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


class TagsView(ModelViewSet):
    """
    View для тэгов
    CRUD для администратора
    Read-only для всех
    """
    queryset = Tags.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = serializers.TagSerializer
