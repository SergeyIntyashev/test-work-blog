from django_filters import rest_framework as filters

from blogs.models import Posts


def add_like_to_post(post: Posts) -> None:
    """
    Инкрементирует лайки поста
    """
    post.likes += 1
    post.save()


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class PostFilter(filters.FilterSet):
    tags = CharFilterInFilter(field_name='tags__title', lookup_expr='in')
    created_at = filters.RangeFilter

    class Meta:
        model = Posts
        fields = ['tags', 'created_at']
