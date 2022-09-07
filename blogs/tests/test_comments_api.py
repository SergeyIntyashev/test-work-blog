from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Comments, Blogs, Posts
from blogs.serializers import CommentSerializer


def create_comment(**kwargs) -> Comments:
    """Создает комментарий"""
    return Comments.objects.create(**kwargs)


class PublicCommentsAPITest(APITestCase):
    """Тестирование методов API для неавторизованных запросов"""

    def setUp(self) -> None:
        self.comments_url = reverse('Comments-list')

        common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        blog = Blogs.objects.create(
            title='Blog title 1',
            description='Blog description 1',
            owner=common_user
        )

        post = Posts.objects.create(
            author=common_user,
            title='Post title',
            body='Post body',
            blog=blog
        )

        create_comment(
            author=common_user,
            body='Test comment 1',
            post=post
        )

        create_comment(
            author=common_user,
            body='Test comment 2',
            post=post
        )

    def test_comments_list(self):
        """Тестирование получения списка комментариев"""

        res = self.client.get(self.comments_url)

        comments = Comments.objects.all()
        serializer = CommentSerializer(comments, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'], serializer.data)

    def test_comment_details(self):
        """Тестирование получения данных конкретного комментария"""

        url = f"{self.comments_url}1/"

        res = self.client.get(url)

        comment = Comments.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['body'], comment.body)

    def test_comment_not_found(self):
        """Тестирование получения несуществующего комментария"""

        url = f"{self.comments_url}4/"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class PrivateCommentsAPITest(APITestCase):
    """Тестирование методов API для авторизованных запросов"""

    def setUp(self) -> None:
        self.comments_url = reverse('Comments-list')

        self.common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            password='adminuserpassword1234!'
        )

        blog = Blogs.objects.create(
            title='Blog title 1',
            description='Blog description 1',
            owner=self.common_user
        )

        self.post = Posts.objects.create(
            author=self.common_user,
            title='Post title',
            body='Post body',
            blog=blog
        )

        create_comment(
            author=self.common_user,
            body='Test comment 1',
            post=self.post
        )

        create_comment(
            author=self.common_user,
            body='Test comment 2',
            post=self.post
        )

        self.client.force_authenticate(user=self.admin_user)

    def test_comment_create_auth_required(self):
        """
        Тестирование создания комментария пользователем
         не являющимся администратором
        """

        self.client.force_authenticate(user=self.common_user)

        res = self.client.post(self.comments_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_comment_create(self):
        """
        Тестирование создания комментария пользователем
        являющимся администратором
        """

        payload = {
            'body': 'Test comment',
            'post': self.post.id
        }

        res = self.client.post(self.comments_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['author'], self.admin_user.id)
        self.assertEqual(res.data['post'], self.post.id)
        self.assertIsNotNone(res.data['created_at'])

    def test_comment_create_not_required(self):
        """
        Тестирование обязательного заполнения полей body и post
        при создании комментария
        """

        res = self.client.post(self.comments_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('body', res.data)
        self.assertIn('post', res.data)

    def test_comment_delete_not_admin(self):
        """
        Тестирование неудачного удаления комментария
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.comments_url}2/"

        res = self.client.delete(url)

        comments = Comments.objects.all()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(comments), 2)

    def test_comment_delete(self):
        """
        Тестирование удаления комментария пользователем являющимся админом
        """

        url = f"{self.comments_url}1/"

        res = self.client.delete(url)

        comments = Comments.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(comments), 1)

    def test_comment_delete_not_exists(self):
        """
        Тестирование удаления несуществующего комментария
        """

        url = f"{self.comments_url}4/"

        res = self.client.delete(url)

        comments = Comments.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(comments), 2)

    def test_comment_update_not_admin(self):
        """
        Тестирование обновления комментария
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.comments_url}2/"

        payload = {
            'body': 'Comment update test',
            'post': self.post.id,
        }

        res = self.client.put(url, payload)

        comment = Comments.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(comment.body, payload['body'])

    def test_comment_update(self):
        """
        Тестирование обновления комментария пользователем являющимся админом
        """

        url = f"{self.comments_url}1/"

        payload = {
            'body': 'Comment update test',
            'post': self.post.id,
        }

        res = self.client.put(url, payload)

        comment = Comments.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['body'], 'Comment update test')
        self.assertEqual(res.data['body'], comment.body)

    def test_comment_update_not_exists(self):
        """
        Тестирование обновления несуществующего комментария
        """

        url = f"{self.comments_url}4/"

        payload = {
            'body': 'Comment update test',
            'post': self.post.id,
        }

        res = self.client.put(url, payload)

        comments = Comments.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(comments), 2)
        self.assertNotEqual(payload['body'], comments.get(id=1).body)

    def test_comment_partial_update_not_admin(self):
        """
        Тестирование частичного обновления комментария
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.comments_url}2/"

        new_body = 'Test partial update'

        comment = Comments.objects.get(id=2)
        comment.description = new_body

        serializer = CommentSerializer(comment)

        res = self.client.patch(url, serializer.data)

        comment.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(comment.body, new_body)

    def test_comment_partial_update(self):
        """
        Тестирование частичного обновления
        комментария пользователем являющимся админом
        """

        url = f"{self.comments_url}1/"

        new_body = 'Test partial update'

        comment = Comments.objects.get(id=1)
        comment.body = new_body

        serializer = CommentSerializer(comment)

        res = self.client.patch(url, serializer.data)

        comment.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['body'], new_body)
        self.assertEqual(new_body, comment.body)

    def test_comment_partial_update_not_exists(self):
        """
        Тестирование неудачного частичного обновления
        несуществующего комментария
        """

        url = f"{self.comments_url}4/"

        new_body = 'Test partial update'

        comment = Comments.objects.get(id=1)
        comment.description = new_body

        serializer = CommentSerializer(comment)

        res = self.client.patch(url, serializer.data)

        comment.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(comment.body, new_body)
