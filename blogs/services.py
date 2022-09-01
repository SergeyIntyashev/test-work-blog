from rest_framework import status, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from blogs.models import Blogs, Posts
from users.models import CustomUser


def user_can_publish_post(blog_id: int, user: CustomUser) -> bool:
    """
    Проверяет является ли пользователь владельцем или автором блога
    """
    blog = get_object_or_404(Blogs, id=blog_id)

    return bool((blog.owner == user) or (user in blog.authors.all()))


def check_and_get_post(post_id: int, blog_id: int, request: Request) -> Posts:
    """
    Проверяет пост на наличие и соответствие его блогу,
    если пост найден и принадлежит блогу возвращает его
    """
    post = get_object_or_404(Posts, id=post_id)

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
