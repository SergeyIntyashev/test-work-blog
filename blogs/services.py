from rest_framework import status, exceptions
from rest_framework.generics import get_object_or_404

from blogs.models import Posts, Blogs
from users.models import CustomUser


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


def get_added_authors_to_blog(authors: list[CustomUser],
                              current_user: CustomUser,
                              blog: Blogs) -> list[CustomUser]:
    blog_authors = blog.authors

    for author in authors:
        if (author != current_user) or (author not in blog_authors):
            blog_authors.add(author)

    return blog_authors


def get_added_subscriptions_to_blog(current_user: CustomUser,
                                    blog: Blogs) -> list[CustomUser]:

    blog_subscriptions = blog.subscriptions

    if current_user not in blog_subscriptions:
        blog_subscriptions.add(current_user)

    return blog_subscriptions
