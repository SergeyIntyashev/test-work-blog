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

    def test_blog_list(self):
        res = self.client.get(self.blog_url)

        blogs = Blogs.objects.all()
        serializer = BlogSerializer(blogs, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'], serializer.data)

    def test_blog_details(self):
        url = f"{self.blog_url}1/"

        res = self.client.get(url)

        blog = Blogs.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], blog.title)
        self.assertEqual(res.data['description'], blog.description)

    def test_blog_not_found(self):
        url = f"{self.blog_url}4/"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
