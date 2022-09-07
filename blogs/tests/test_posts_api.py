from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from blogs.models import Comments, Blogs, Posts
from blogs.serializers import PostSerializer


def create_post(**kwargs) -> Posts:
    """Создает пост"""
    return Posts.objects.create(**kwargs)


class PublicPostsAPITest(APITestCase):
    """Тестирование методов API для неавторизованных запросов"""

    def setUp(self) -> None:
        self.posts_url = reverse('Posts-list')

        common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        blog = Blogs.objects.create(
            title='Blog title 1',
            description='Blog description 1',
            owner=common_user
        )

        create_post(
            author=common_user,
            title='Post title 1',
            body='Post body 1',
            is_published=True,
            blog=blog
        )

        create_post(
            author=common_user,
            title='Post title 2',
            body='Post body 2',
            is_published=True,
            blog=blog
        )

        create_post(
            author=common_user,
            title='Post title 3',
            body='Post body 3',
            blog=blog
        )

    def test_posts_list(self):
        """Тестирование получения списка опубликованных постов"""

        res = self.client.get(self.posts_url)

        posts = Posts.objects.filter(is_published=True).all()
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['results'], serializer.data)

    def test_post_details(self):
        """Тестирование получения данных конкретного поста"""

        url = f"{self.posts_url}1/"

        res = self.client.get(url)

        post = Posts.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['body'], post.body)
        self.assertEqual(res.data['title'], post.title)

    def test_post_increase_views(self):
        """Тестирование увеличения количества просмотров поста"""

        url = f"{self.posts_url}1/"

        post = Posts.objects.get(id=1)
        self.assertEqual(post.views, 0)

        res = self.client.get(url)

        post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.views, 1)
        self.assertEqual(res.data['body'], post.body)

    def test_post_not_found(self):
        """Тестирование получения несуществующего поста"""

        url = f"{self.posts_url}4/"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class PrivatePostsAPITest(APITestCase):
    """Тестирование методов API для авторизованных запросов"""

    def setUp(self) -> None:
        self.posts_url = reverse('Posts-list')

        self.common_user = get_user_model().objects.create_common_user(
            username='commonuser',
            password='commonuserpassword1234!'
        )

        self.common_user2 = get_user_model().objects.create_common_user(
            username='commonuser2',
            password='commonuser2password1234!'
        )

        self.common_user3 = get_user_model().objects.create_common_user(
            username='commonuser3',
            password='commonuser3password1234!'
        )

        self.blog = Blogs.objects.create(
            title='Blog title 1',
            description='Blog description 1',
            owner=self.common_user
        )

        self.blog.authors.add(self.common_user2)
        self.blog.save()

        create_post(
            author=self.common_user,
            title='Post title 1',
            body='Post body 1',
            is_published=True,
            blog=self.blog
        )

        create_post(
            author=self.common_user,
            title='Post title 2',
            body='Post body 2',
            is_published=True,
            blog=self.blog
        )

        create_post(
            author=self.common_user,
            title='Post title 3',
            body='Post body 3',
            blog=self.blog
        )

        create_post(
            author=self.common_user2,
            title='Post title 4',
            body='Post body 4',
            is_published=True,
            blog=self.blog
        )

        self.posts_count = len(Posts.objects.all())
        self.client.force_authenticate(user=self.common_user)

    def test_posts_list_my(self):
        """Тестирование получения списка постов пользователя"""

        url = f'{self.posts_url}my'
        res = self.client.get(url)

        posts = Posts.objects.filter(author_id=self.common_user.id).all()
        serializer = PostSerializer(posts, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 3)
        self.assertEqual(res.data['results'], serializer.data)

    def test_post_add_like_auth_required(self):
        """
        Тестирование добавления лайка посту неавторизованным пользователем
        """

        self.client.logout()

        url = f'{self.posts_url}1/add-like'
        res = self.client.patch(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_add_like(self):
        """
        Тестирование добавления лайка посту авторизованному пользователю
        """

        url = f'{self.posts_url}1/add-like'

        post = Posts.objects.get(id=1)

        self.assertEqual(post.likes, 0)

        res = self.client.patch(url)

        post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.likes, 1)

    def test_post_add_comment_auth_required(self):
        """
        Тестирование добавления комментария посту
        неавторизованным пользователем
        """

        self.client.logout()

        url = f'{self.posts_url}1/add-comment'

        payload = {
            'body': 'Test comment create'
        }

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(Comments.objects.all()), 0)

    def test_post_add_comment_content_required(self):
        """
        Тестирование добавления комментария посту
        без заполнения обязательных полей
        """

        url = f'{self.posts_url}1/add-comment'

        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('body', res.data)
        self.assertEqual(len(Comments.objects.all()), 0)

    def test_post_add_comment(self):
        """
        Тестирование добавления комментария посту
        """

        url = f'{self.posts_url}1/add-comment'

        payload = {
            'body': 'Test comment create'
        }

        res = self.client.post(url, payload)

        comments = Comments.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments.first().body, payload['body'])

    def test_post_create_auth_required(self):
        """
        Тестирование создания поста неаутентифицированным пользователем
        """

        self.client.logout()

        payload = {
            'title': 'Test post create title',
            'body': 'Test post create body',
            'blog': self.blog.id
        }

        res = self.client.post(self.posts_url, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_create_not_blog_author(self):
        """
        Тестирование создания поста пользователем не являющимся автором блога
        """

        self.client.force_authenticate(user=self.common_user3)

        payload = {
            'title': 'Test post create title',
            'body': 'Test post create body',
            'blog': self.blog.id
        }

        res = self.client.post(self.posts_url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_create_of_blog_author(self):
        """
        Тестирование создания поста пользователем
        являющимся автором блога
        """

        self.client.force_authenticate(user=self.common_user2)

        payload = {
            'title': 'Test post create title',
            'body': 'Test post create body',
            'blog': self.blog.id
        }

        res = self.client.post(self.posts_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['author'], self.common_user2.id)
        self.assertEqual(res.data['blog'], self.blog.id)
        self.assertIsNone(res.data['created_at'])

    def test_post_create_of_blog_owner(self):
        """
        Тестирование создания поста пользователем
        являющимся владельцем блога
        """

        self.client.force_authenticate(user=self.common_user)

        payload = {
            'title': 'Test post create title',
            'body': 'Test post create body',
            'blog': self.blog.id
        }

        res = self.client.post(self.posts_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['author'], self.common_user.id)
        self.assertEqual(res.data['blog'], self.blog.id)
        self.assertIsNone(res.data['created_at'])

    def test_post_create_is_published_filled(self):
        """
        Тестирование автозаполнения даты создания поста
        """

        payload = {
            'title': 'Test post create title',
            'body': 'Test post create body',
            'blog': self.blog.id,
            'is_published': True
        }

        res = self.client.post(self.posts_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.data['created_at'])

    def test_post_create_not_required(self):
        """
        Тестирование обязательного заполнения полей при создании поста
        """

        res = self.client.post(self.posts_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data)
        self.assertIn('body', res.data)
        self.assertIn('blog', res.data)

    def test_post_delete_auth_required(self):
        """
        Тестирование удаления поста неавторизованным пользователем
        """

        self.client.logout()

        url = f"{self.posts_url}2/"

        res = self.client.delete(url)

        posts = Posts.objects.all()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(posts), self.posts_count)

    def test_post_delete_of_not_owner(self):
        """
        Тестирование удаления поста пользователем не являющимся автором
        """

        self.client.force_authenticate(user=self.common_user2)

        url = f"{self.posts_url}1/"

        res = self.client.delete(url)

        posts = Posts.objects.all()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(posts), self.posts_count)

    def test_post_delete_of_owner(self):
        """
        Тестирование удаления поста пользователем являющимся автором поста
        """

        url = f"{self.posts_url}2/"

        res = self.client.delete(url)

        posts = Posts.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(posts), 3)

    def test_post_delete_not_exists(self):
        """
        Тестирование удаления несуществующего поста
        """

        url = f"{self.posts_url}6/"

        res = self.client.delete(url)

        posts = Posts.objects.all()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(posts), self.posts_count)

    def test_post_update_auth_required(self):
        """
        Тестирование обновления поста неавторизованным пользователем
        """

        self.client.logout()

        url = f"{self.posts_url}2/"

        payload = {
            'title': 'Test post update title',
            'body': 'Test post update body',
            'blog': self.blog.id,
            'is_published': True
        }

        res = self.client.put(url, payload)

        post = Posts.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(post.title, payload['title'])
        self.assertNotEqual(post.body, payload['body'])

    def test_post_update_of_not_owner(self):
        """
        Тестирование обновления поста пользователем не являющимся автором
        """

        self.client.force_authenticate(user=self.common_user2)

        url = f"{self.posts_url}1/"

        payload = {
            'title': 'Test post update title',
            'body': 'Test post update body',
            'blog': self.blog.id,
            'is_published': True
        }

        res = self.client.put(url, payload)

        post = Posts.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(post.title, payload['title'])
        self.assertNotEqual(post.body, payload['body'])

    def test_post_update_of_owner(self):
        """
        Тестирование обновления поста пользователем являющимся автором поста
        """

        url = f"{self.posts_url}2/"

        payload = {
            'title': 'Test post update title',
            'body': 'Test post update body',
            'blog': self.blog.id,
            'is_published': True
        }

        res = self.client.put(url, payload)

        post = Posts.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.body, payload['body'])

    def test_post_update_not_exists(self):
        """
        Тестирование обновления несуществующего поста
        """

        url = f"{self.posts_url}6/"

        payload = {
            'title': 'Test post update title',
            'body': 'Test post update body',
            'blog': self.blog.id,
            'is_published': True
        }

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_update_is_published_filled(self):
        """
        Тестирование автозаполнения даты создания поста при его обновлении
        """

        url = f"{self.posts_url}3/"

        payload = {
            'title': 'Test post update title',
            'body': 'Test post update body',
            'blog': self.blog.id,
            'is_published': True
        }

        post = Posts.objects.get(id=3)
        self.assertIsNone(post.created_at)

        res = self.client.put(url, payload)

        post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(post.created_at)

    def test_post_partial_update_auth_required(self):
        """
        Тестирование частичного обновления поста неавторизованным пользователем
        """

        self.client.logout()

        url = f"{self.posts_url}2/"

        payload = {
            'title': 'Test post partial update title',
        }

        res = self.client.patch(url, payload)

        post = Posts.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(post.title, payload['title'])

    def test_post_partial_update_of_not_owner(self):
        """
        Тестирование частичного обновления поста
        пользователем не являющимся автором
        """

        self.client.force_authenticate(user=self.common_user2)

        url = f"{self.posts_url}1/"

        payload = {
            'title': 'Test post partial update title',
        }

        res = self.client.patch(url, payload)

        post = Posts.objects.get(id=1)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(post.title, payload['title'])

    def test_post_partial_update_of_owner(self):
        """
        Тестирование частичного обновления поста
        пользователем являющимся автором поста
        """

        url = f"{self.posts_url}2/"

        payload = {
            'title': 'Test post partial update title',
        }

        res = self.client.patch(url, payload)

        post = Posts.objects.get(id=2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.title, payload['title'])

    def test_post_partial_update_not_exists(self):
        """
        Тестирование частичного обновления несуществующего поста
        """

        url = f"{self.posts_url}6/"

        payload = {
            'title': 'Test post partial update title',
        }

        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_partial_update_is_published_filled(self):
        """
        Тестирование автозаполнения даты создания поста
        при его частичного обновлении
        """

        url = f"{self.posts_url}3/"

        payload = {
            'title': 'Test post partial update title',
            'body': 'Test post partial update body',
            'blog': self.blog.id,
            'is_published': True
        }

        post = Posts.objects.get(id=3)
        self.assertIsNone(post.created_at)

        res = self.client.put(url, payload)

        post.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(post.created_at)
