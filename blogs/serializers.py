from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from blogs.models import Blogs, Posts, Comments, Tags
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о пользователе
    """

    class Meta:
        model = CustomUser
        fields = ['username']


class BlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для блогов
    """

    owner = UserSerializer(read_only=True)
    authors = UserSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Blogs
        fields = '__all__'


class AddAuthorsToBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления авторов в блог
    """

    class Meta:
        model = Blogs
        fields = ['authors']


class TagSerializer(PrimaryKeyRelatedField, serializers.ModelSerializer):
    """
    Сериализатор для тэгов
    """

    class Meta:
        model = Tags
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для постов
    """

    author = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    likes = serializers.IntegerField(read_only=True)
    views = serializers.IntegerField(read_only=True)
    blog = BlogSerializer(read_only=True)
    tags = TagSerializer(many=True, queryset=Tags.objects.all())

    class Meta:
        model = Posts
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев
    """
    author = UserSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    post = PostSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = '__all__'
