from collections import namedtuple
from typing import Type

from django.db.models import F
from django_filters import rest_framework as filters

from blogs.models import Posts

Actions = namedtuple('Actions',
                     ['list', 'create', 'retrieve', 'update', 'delete'])


def increase_likes_of_post(post: Posts) -> None:
    """
    Инкрементирует лайки поста
    """

    post.likes = F('likes') + 1
    post.save(update_fields=('likes',))


def increase_views_of_post(post: Posts, user) -> None:
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


def get_views_actions_model(view) -> Actions:
    return Actions(
        list=view.as_view({
            'get': 'list',
        }),
        create=view.as_view({
            'post': 'create',
        }),
        retrieve=view.as_view({
            'get': 'retrieve',
        }),
        update=view.as_view({
            'put': 'update',
            'patch': 'partial_update',
        }),
        delete=view.as_view({
            'delete': 'destroy'
        })
    )
