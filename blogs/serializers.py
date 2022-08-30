from rest_framework import serializers

from blogs.models import Blogs


class BlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для блогов
    """

    class Meta:
        model = Blogs
        fields = ['title', 'description', 'owner', 'authors']


class AddAuthorsToBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления авторов в блог
    """

    class Meta:
        model = Blogs
        fields = ['id', 'authors']