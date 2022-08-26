from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone


class Blogs(models.Model):
    """
    Модель блогов
    """
    title = models.CharField(max_length=150, blank=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, auto_now=True)
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     blank=True,
                                     null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              db_index=True)

    class Meta:
        ordering = ('-created_at')
        indexes = [
            GinIndex(fields=['title']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f"id :{self.id} owner: {self.owner.username}"


class Tags(models.Model):
    """
    Модель тегов для постов
    """
    title = models.CharField(max_length=150, blank=False, db_index=True)

    def __str__(self):
        return self.title


class Posts(models.Model):
    """
    Модель постов
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE,
                               db_index=True)
    title = models.CharField(max_length=150, blank=False)
    body = models.TextField(blank=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(editable=False, blank=True)
    likes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    blog = models.ForeignKey(Blogs, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tags, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
        Заполняет поле created_at, если оно пустое
        и поле is_published = True
        """
        if self.is_published and not self.created_at:
            self.created_at = timezone.now()

        super(Posts, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-created_at')
        indexes = [
            GinIndex(fields=['title']),
            models.Index(fields=['created_at'])
        ]

    def __str__(self):
        return f"id :{self.id} author: {self.author.username} " \
               f"blog: {self.blog.id}"


class Comments(models.Model):
    """
    Модель комментариев для постов
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL)
    body = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at')
        order_with_respect_to = 'post'

    def __str__(self):
        return f"id: {self.id} author: {self.author.username} " \
               f"post: {self.post.id}"
