from rest_framework import status, exceptions
from rest_framework.generics import get_object_or_404

from blogs.models import Posts


def check_and_get_post(post_id: int, blog_id: int) -> Posts:
    """
    Проверяет пост на наличие и соответствие его блогу,
    если пост найден и принадлежит блогу возвращает его
    """
    post = get_object_or_404(Posts.objects.select_related('blog'), id=post_id)

    if not post.blog.id == blog_id:
        exceptions.PermissionDenied(
            detail="The current post does not belong to blog",
            code=status.HTTP_403_FORBIDDEN
        )

    return post


def add_like_to_post(post: Posts) -> None:
    """
    Инкрементирует лайки поста
    """
    post.likes += 1
    post.save()
