from django.contrib.auth import get_user_model
from django.test import TestCase

from blogs import models


def create_user(username: str, password: str) -> get_user_model():
    """Создает пользователя"""
    return get_user_model().objects.create_common_user(username, password)


class BlogsTest(TestCase):

    def setUp(self) -> None:
        self.user_owner = create_user(
            username='testuserowner',
            password='testpasswordowner12412!'
        )

        self.user_author = create_user(
            username='testuserauthor',
            password='testpasswordauthor12412!'
        )

        self.user_subscription = create_user(
            username='testusersubscription',
            password='testpasswordsubscription12412!'
        )

    def test_blog_str(self):
        """Тестирование строкового представления"""

        blog = models.Blogs.objects.create(
            owner=self.user_owner,
            title='Blog title',
            description='Blog description',
        )

        self.assertEqual(str(blog),
                         f"id: {blog.id} owner: {blog.owner.username}")

    def test_blog_content(self):
        """Тестирование содержимого полей"""
        blog = models.Blogs.objects.create(
            owner=self.user_owner,
            title='Blog title',
            description='Blog description'
        )

        self.assertEqual(blog.title, 'Blog title')
        self.assertEqual(blog.description, 'Blog description')
        self.assertEqual(blog.owner, self.user_owner)
        self.assertIsNotNone(blog.created_at)
        self.assertIsNotNone(blog.updated_at)
        self.assertEqual(len(blog.authors.all()), 0)
        self.assertEqual(len(blog.subscriptions.all()), 0)

    def test_blog_authors_subscriptions(self):
        """Тестирование добавления авторов и подписчиков"""
        blog = models.Blogs.objects.create(
            owner=self.user_owner,
            title='Blog title',
            description='Blog description'
        )

        blog.authors.add(self.user_author)
        blog.subscriptions.add(self.user_subscription)

        blog_author = blog.authors.all()[0]
        blog_subscription = blog.subscriptions.all()[0]

        self.assertEqual(blog_author, self.user_author)
        self.assertEqual(blog_subscription, self.user_subscription)
        self.assertEqual(len(blog.authors.all()), 1)
        self.assertEqual(len(blog.subscriptions.all()), 1)


class TagsTest(TestCase):

    def test_tag_str(self):
        """Тестирование строкового представления"""

        tag = models.Tags.objects.create(
            title='Tag test',
        )

        self.assertEqual(str(tag), tag.title)

    def test_tag_content(self):
        """Тестирование содержимого полей"""
        tag = models.Tags.objects.create(
            title='Tag title',
        )

        self.assertEqual(tag.title, 'Tag title')


class PostsTest(TestCase):

    def setUp(self) -> None:
        self.user_owner = create_user(
            username='testuserowner',
            password='testpasswordowner12412!'
        )

        self.user_author = create_user(
            username='testuserauthor',
            password='testpasswordauthor12412!'
        )

        self.blog = models.Blogs.objects.create(
            owner=self.user_owner,
            title='Blog title',
            description='Blog description'
        )

        self.tag = models.Tags.objects.create(
            title='Tag title',
        )

    def test_post_str(self):
        """Тестирование строкового представления"""

        post = models.Posts.objects.create(
            author=self.user_author,
            title='Post title',
            body='Post body',
            blog=self.blog
        )
        self.assertEqual(str(post),
                         f"id: {post.id} author: {post.author.username} "
                         f"blog: {post.blog.id}")

    def test_post_content(self):
        """Тестирование содержимого полей"""

        post = models.Posts.objects.create(
            author=self.user_author,
            title='Post title',
            body='Post body',
            blog=self.blog,
            views=10
        )

        self.assertEqual(post.title, 'Post title')
        self.assertEqual(post.body, 'Post body')
        self.assertEqual(post.author, self.user_author)
        self.assertEqual(post.blog, self.blog)
        self.assertIsNone(post.created_at)
        self.assertFalse(post.is_published)
        self.assertEqual(post.likes, 0)
        self.assertEqual(post.views, 10)

    def test_blog_authors_subscriptions(self):
        """Тестирование добавления тегов"""

        post = models.Posts.objects.create(
            author=self.user_author,
            title='Post title',
            body='Post body',
            blog=self.blog
        )

        post.tags.add(self.tag)

        post_tag = post.tags.all()[0]

        self.assertEqual(post_tag, self.tag)
        self.assertEqual(len(post.tags.all()), 1)


class CommentsTest(TestCase):

    def setUp(self) -> None:
        user_owner = create_user(
            username='testuserowner',
            password='testpasswordowner12412!'
        )

        user_post_author = create_user(
            username='testuserpostauthor',
            password='testpasswordpostauthor12412!'
        )

        self.user_comment_author = create_user(
            username='testuserccommentauthor',
            password='testpasswordcommentauthor12412!'
        )

        blog = models.Blogs.objects.create(
            owner=user_owner,
            title='Blog title',
            description='Blog description'
        )

        self.post = models.Posts.objects.create(
            author=user_post_author,
            title='Post title',
            body='Post body',
            blog=blog
        )

    def test_comment_str(self):
        """Тестирование строкового представления"""

        comment = models.Comments.objects.create(
            author=self.user_comment_author,
            body='Comment body',
            post=self.post
        )
        self.assertEqual(str(comment),
                         f"id: {comment.id} author: {comment.author.username} "
                         f"post: {comment.post.id}")

    def test_post_content(self):
        """Тестирование содержимого полей"""

        comment = models.Comments.objects.create(
            author=self.user_comment_author,
            body='Comment body',
            post=self.post
        )

        self.assertEqual(comment.body, 'Comment body')
        self.assertEqual(comment.author, self.user_comment_author)
        self.assertEqual(comment.post, self.post)
        self.assertIsNotNone(comment.created_at)
