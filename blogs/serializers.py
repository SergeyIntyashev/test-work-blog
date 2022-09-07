from django.contrib.auth import get_user_model
from rest_framework import serializers

from blogs.models import Blogs, Posts, Comments, Tags


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о пользователе
    """

    class Meta:
        model = get_user_model()
        fields = ['username']


class BlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для блогов
    """

    class Meta:
        model = Blogs
        fields = '__all__'
        read_only_fields = (
            'id',
            'owner',
            'authors',
            'subscriptions',
            'created_at',
            'updated_at'
        )


class AddAuthorsToBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления авторов в блог
    """

    def update(self, instance, validated_data):
        authors = validated_data.pop('authors')
        current_user = self.context['request'].user

        for author in authors:
            if (author != current_user) \
                    and (author not in instance.authors.all()):
                instance.authors.add(author)

        return instance

    class Meta:
        model = Blogs
        fields = ['authors']


class AddSubscriptionsToBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления подписчиков в блог
    """

    def update(self, instance, validated_data):
        current_user = self.context['request'].user

        if current_user not in instance.subscriptions.all():
            instance.subscriptions.add(current_user)

        return instance

    class Meta:
        model = Blogs
        fields = ['subscriptions']


class TagSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Posts
        fields = '__all__'
        read_only_fields = (
            'id',
            'author',
            'likes',
            'views',
            'created_at',
        )


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев
    """

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = (
            'id',
            'author',
            'created_at',
        )


class AddCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления комментариев
    """

    class Meta:
        model = Comments
        fields = '__all__'
        read_only_fields = (
            'id',
            'author',
            'post',
            'created_at',
        )
