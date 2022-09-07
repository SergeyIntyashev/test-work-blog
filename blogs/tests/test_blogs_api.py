from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Blogs
from blogs.serializers import BlogSerializer


def create_blog(**kwargs) -> Blogs:
    """Создает блог"""
    return Blogs.objects.create(**kwargs)


class PublicBlogAPITest(APITestCase):
    """Тестирование методов API для неавторизованных запросов"""

    def setUp(self) -> None:
        self.blog_url = reverse('Blogs-list')

        self.common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        create_blog(
            title='Blog title 1',
            description='Blog description 1',
            owner=self.common_user
        )

        create_blog(
            title='Blog title 2',
            description='Blog description 2',
            owner=self.common_user
        )

    def test_blog_list(self):
        """Тестрование получения списка блогов"""

        res = self.client.get(self.blog_url)

        blogs = Blogs.objects.all()
        serializer = BlogSerializer(blogs, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'], serializer.data)

    def test_blog_details(self):
        """Тестирование получения данных конкретного блога"""

        url = f"{self.blog_url}1/"

        res = self.client.get(url)

        blog = Blogs.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], blog.title)
        self.assertEqual(res.data['description'], blog.description)

    def test_blog_not_found(self):
        """Тестирование получения несущестсвующего блога"""

        url = f"{self.blog_url}4/"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class PrivateBlogsAPITest(APITestCase):
    """Тестирование методов API для авторизованных запросов"""

    def setUp(self) -> None:
        self.blog_url = reverse('Blogs-list')
        self.favorite_url = reverse('my-favorite-blogs')

        self.common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        self.common_user2 = get_user_model().objects.create_common_user(
            username='commonuser2',
            password='commonuserpassword1234!'
        )

        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            password='adminuserpassword1234!'
        )

        create_blog(
            title='Blog title 1',
            description='Blog description 1',
            owner=self.common_user
        )

        create_blog(
            title='Blog title 2',
            description='Blog description 2',
            owner=self.common_user2
        )

        self.client.force_authenticate(user=self.common_user)

    def test_blog_create_auth_required(self):
        """Тестирование необходимости аутентификации при создании блога"""

        self.client.logout()
        res = self.client.post(self.blog_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blog_create_not_required(self):
        """
        Тестирование обязательного заполнения поля title при создании блога
        """

        res = self.client.post(self.blog_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)

    def test_blog_create(self):
        """
        Тестирование успешного создания блога
        """

        payload = {
            'title': 'Blog test 3',
            'description': 'Blog test 3 description'
        }

        res = self.client.post(self.blog_url, payload)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)
        self.assertEqual(len(blogs), 3)

    def test_blogs_delete_not_owner(self):
        """
        Тестирование неудачного удаления блога
        пользователем не являющимся автором
        """

        url = f"{self.blog_url}2/"

        res = self.client.delete(url)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(blogs), 2)

    def test_blogs_delete(self):
        """
        Тестирование успешного удаления блога пользователем являющимся автором
        """

        url = f"{self.blog_url}1/"

        res = self.client.delete(url)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(blogs), 1)

    def test_blogs_delete_not_exists(self):
        """
        Тестирование неудачного удаления несуществующего блога
        """

        url = f"{self.blog_url}4/"

        res = self.client.delete(url)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(blogs), 2)

    def test_blogs_update_not_owner(self):
        """
        Тестирование неудачного обновления блога
        пользователем не являющимся автором
        """

        url = f"{self.blog_url}2/"

        payload = {
            'title': 'Blog update test',
            'description': 'Blog update test description'
        }

        res = self.client.put(url, payload)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(blogs.get(id=2).title, payload['title'])

    def test_blogs_update(self):
        """
        Тестирование успешного обновления блога пользователем являющимся автором
        """

        url = f"{self.blog_url}1/"

        payload = {
            'title': 'Blog update test',
            'description': 'Blog update test description'
        }

        res = self.client.put(url, payload)

        blog = Blogs.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Blog update test')
        self.assertEqual(res.data['title'], blog.title)

    def test_blogs_update_not_exists(self):
        """
        Тестирование неудачного обновления несуществующего блога
        """

        url = f"{self.blog_url}4/"

        payload = {
            'title': 'Blog update test',
            'description': 'Blog update test description'
        }

        res = self.client.put(url, payload)

        blogs = Blogs.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(blogs), 2)
        self.assertNotEqual(payload['title'], blogs.get(id=1).title)

    def test_blogs_partial_update_not_owner(self):
        """
        Тестирование неудачного частичного обновления блога
        пользователем не являющимся автором
        """

        url = f"{self.blog_url}2/"

        new_description = 'Test partial update'

        blog = Blogs.objects.get(id=2)
        blog.description = new_description

        serializer = BlogSerializer(blog)

        res = self.client.patch(url, serializer.data)

        blog.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(blog.title, new_description)

    def test_blogs_partial_update(self):
        """
        Тестирование успешного частичного обновления
        блога пользователем являющимся автором
        """

        url = f"{self.blog_url}1/"

        new_description = 'Test partial update'

        blog = Blogs.objects.get(id=1)
        blog.description = new_description

        serializer = BlogSerializer(blog)

        res = self.client.patch(url, serializer.data)

        blog.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['description'], new_description)
        self.assertEqual(new_description, blog.description)

    def test_blogs_partial_update_not_exists(self):
        """
        Тестирование неудачного частичного обновления несуществующего блога
        """

        url = f"{self.blog_url}4/"

        new_description = 'Test partial update'

        blog = Blogs.objects.get(id=1)
        blog.description = new_description

        serializer = BlogSerializer(blog)

        res = self.client.patch(url, serializer.data)

        blog.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(blog.description, new_description)

    def test_blog_add_authors(self):
        """Тестирование добавления авторов в блог"""

        url = f"{self.blog_url}1/add-authors"

        payload = {
            'authors': [
                2
            ]
        }

        res = self.client.patch(url, payload)

        blog = Blogs.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(blog.authors.all()), 1)
        self.assertEqual(blog.authors.all()[0], self.common_user2)

    def test_blog_add_authors_not_exist(self):
        """Тестирование добавления авторов в несуществующий блог"""

        url = f"{self.blog_url}4/add-authors"

        payload = {
            'authors': [
                2
            ]
        }

        res = self.client.patch(url, payload)

        blog = Blogs.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(blog.authors.all()), 0)

    def test_blog_subscribe(self):
        """Тестирование подписки на блог"""

        url = f"{self.blog_url}2/subscribe"

        res = self.client.patch(url)

        blog = Blogs.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(blog.subscriptions.all()), 1)
        self.assertEqual(blog.subscriptions.all()[0], self.common_user)

    def test_blog_subscribe_not_exist(self):
        """Тестирование подписки на несуществующий блог"""

        url = f"{self.blog_url}4/subscribe"

        res = self.client.patch(url)

        blog = Blogs.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(blog.subscriptions.all()), 0)

    def test_blog_favorites(self):
        """Тестирование получения списка блогов
        на которых подписан пользователь"""

        url = f"{self.blog_url}2/subscribe"
        res = self.client.patch(url)

        url_favorites = f"{self.blog_url}favorites"
        res_favorites = self.client.get(url_favorites)

        blog = Blogs.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_favorites.data['results']), 1)
        self.assertEqual(res_favorites.data['results'][0]['title'], blog.title)
