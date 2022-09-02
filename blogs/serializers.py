from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from blogs.models import Blogs, Posts, Comments, Tags


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о пользователе
    """

    class Meta:
        model = settings.AUTH_USER_MODEL
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

    def update(self, instance, validated_data):
        authors = validated_data.pop('authors')
        current_user = self.context['request'].user

        for author in authors:
            if author != current_user:
                instance.authors.add(author)

        return instance

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
