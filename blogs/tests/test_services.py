from django.contrib.auth import get_user_model
from django.test import TestCase

from blogs import models
from blogs.services import increase_likes_of_post, increase_views_of_post


def create_user(username: str, password: str) -> get_user_model():
    """Создает пользователя"""
    return get_user_model().objects.create_common_user(username, password)


class TestServices(TestCase):

    def setUp(self) -> None:
        self.user_owner = create_user(
            username='testuserowner',
            password='testpasswordowner12412!'
        )

        self.user_author = create_user(
            username='testuserpostauthor',
            password='testpasswordpostauthor12412!'
        )

        blog = models.Blogs.objects.create(
            owner=self.user_owner,
            title='Blog title',
            description='Blog description'
        )

        self.post = models.Posts.objects.create(
            author=self.user_author,
            title='Post title',
            body='Post body',
            blog=blog
        )

    def test_increase_likes_of_post(self):
        increase_likes_of_post(self.post)
        self.post.refresh_from_db()

        self.assertEqual(self.post.likes, 1)

    def test_increase_views_of_post(self):
        increase_views_of_post(self.post, self.user_owner)
        increase_views_of_post(self.post, self.user_author)
        self.post.refresh_from_db()

        self.assertEqual(self.post.views, 1)
