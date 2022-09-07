from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Tags
from blogs.serializers import TagSerializer


def create_tag(**kwargs) -> Tags:
    """Создает тэг"""
    return Tags.objects.create(**kwargs)


class PublicTagsAPITest(APITestCase):

    def setUp(self) -> None:
        self.tags_url = reverse('Tags-list')

        create_tag(
            title='Tag 1',
        )

        create_tag(
            title='Tag 2',
        )

    def test_tags_list(self):
        """Тестрование получения списка тэгов"""

        res = self.client.get(self.tags_url)

        tags = Tags.objects.all()
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'], serializer.data)

    def test_tag_details(self):
        """Тестирование получения данных конкретного тэга"""

        url = f"{self.tags_url}1/"

        res = self.client.get(url)

        tag = Tags.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], tag.title)

    def test_tag_not_found(self):
        """Тестирование получения несущестсвующего тэга"""

        url = f"{self.tags_url}4/"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class PrivateTagsAPITest(APITestCase):

    def setUp(self) -> None:
        self.tags_url = reverse('Tags-list')

        self.common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        self.admin_user = get_user_model().objects.create_superuser(
            username='adminuser',
            password='adminuserpassword1234!'
        )

        create_tag(
            title='Tag 1',
        )

        create_tag(
            title='Tag 2',
        )

        self.client.force_authenticate(user=self.admin_user)

    def test_tag_create_not_admin(self):
        """
        Тестирование необходимости аутентификации админа при создании тэга
        """

        self.client.force_authenticate(user=self.common_user)
        res = self.client.post(self.tags_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_tag_create_not_required(self):
        """
        Тестирование обязательного заполнения поля title при создании тэга
        """

        res = self.client.post(self.tags_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)

    def test_tag_create(self):
        """
        Тестирование создания тэга
        """

        payload = {
            'title': 'Tag test 3',
        }

        res = self.client.post(self.tags_url, payload)

        tags = Tags.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)
        self.assertEqual(len(tags), 3)

    def test_tag_delete_not_admin(self):
        """
        Тестирование неудачного удаления тэга
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.tags_url}2/"

        res = self.client.delete(url)

        tags = Tags.objects.all()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(tags), 2)

    def test_tag_delete(self):
        """
        Тестирование удаления тэга пользователем являющимся админом
        """

        url = f"{self.tags_url}1/"

        res = self.client.delete(url)

        tags = Tags.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(tags), 1)

    def test_tag_delete_not_exists(self):
        """
        Тестирование удаления несуществующего тэга
        """

        url = f"{self.tags_url}4/"

        res = self.client.delete(url)

        tags = Tags.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(tags), 2)

    def test_tag_update_not_owner(self):
        """
        Тестирование обновления тэга
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.tags_url}2/"

        payload = {
            'title': 'Tag update test',
        }

        res = self.client.put(url, payload)

        tag = Tags.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(tag.title, payload['title'])

    def test_tag_update(self):
        """
        Тестирование обновления тэга пользователем являющимся админом
        """

        url = f"{self.tags_url}1/"

        payload = {
            'title': 'Tag update test',
        }

        res = self.client.put(url, payload)

        tag = Tags.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Tag update test')
        self.assertEqual(res.data['title'], tag.title)

    def test_tag_update_not_exists(self):
        """
        Тестирование обновления несуществующего тэга
        """

        url = f"{self.tags_url}4/"

        payload = {
            'title': 'Tag update test',
        }

        res = self.client.put(url, payload)

        tags = Tags.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(tags), 2)
        self.assertNotEqual(payload['title'], tags.get(id=1).title)

    def test_tag_partial_update_not_owner(self):
        """
        Тестирование частичного обновления тэга
        пользователем не являющимся админом
        """

        self.client.force_authenticate(user=self.common_user)

        url = f"{self.tags_url}2/"

        new_description = 'Test partial update'

        tag = Tags.objects.get(id=2)
        tag.description = new_description

        serializer = TagSerializer(tag)

        res = self.client.patch(url, serializer.data)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(tag.title, new_description)

    def test_tag_partial_update(self):
        """
        Тестирование частичного обновления
        тэга пользователем являющимся админом
        """

        url = f"{self.tags_url}1/"

        new_title = 'Test partial update'

        tag = Tags.objects.get(id=1)
        tag.title = new_title

        serializer = TagSerializer(tag)

        res = self.client.patch(url, serializer.data)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], new_title)
        self.assertEqual(new_title, tag.title)

    def test_tag_partial_update_not_exists(self):
        """
        Тестирование неудачного частичного обновления несуществующего тэга
        """

        url = f"{self.tags_url}4/"

        new_title = 'Test partial update'

        tag = Tags.objects.get(id=1)
        tag.description = new_title

        serializer = TagSerializer(tag)

        res = self.client.patch(url, serializer.data)

        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(tag.title, new_title)
