from django.db.models import F
from django_filters import rest_framework as filters

from blogs.models import Posts
from users.models import CustomUser


def increase_likes_of_post(post: Posts) -> None:
    """
    Инкрементирует лайки поста
    """

    post.likes = F('likes') + 1
    post.save(update_fields=('likes',))


def increase_views_of_post(post: Posts, user: CustomUser) -> None:
    """
    Инкрементирует просмотры поста,
    в случае, если пользователь не является владельцем блога
    """

    if post.blog.owner != user:
        post.views = F('views') + 1
        post.save(update_fields=('views',))


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    """
    Фильтр для возможности фильтрации по списку
    """
    pass


class PostFilter(filters.FilterSet):
    """
    Фильтр по тэгам и дате создания поста
    """
    tags = CharFilterInFilter(field_name='tags__title', lookup_expr='in')
    created_at = filters.RangeFilter

    class Meta:
        model = Posts
        fields = ['tags', 'created_at']
