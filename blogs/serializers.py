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
    subscriptions = UserSerializer(many=True, read_only=True)
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
