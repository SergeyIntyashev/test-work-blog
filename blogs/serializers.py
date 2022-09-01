from rest_framework import serializers

from blogs.models import Blogs, Posts, Comments, Tags


class CreateBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания блога
    """

    class Meta:
        model = Blogs
        fields = ['title', 'description', 'owner', 'authors']


class AddAuthorsToBlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления авторов в блог
    """

    def update(self, instance, validated_data):
        authors = validated_data.pop('authors')
        for author in authors:
            instance.authors.add(author)
        return instance

    class Meta:
        model = Blogs
        fields = ['authors']


class PublishPostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публикации поста в блог
    """

    class Meta:
        model = Posts
        fields = ['title', 'body', 'is_published', 'blog', 'tags']


class CreateCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания комментариев
    """

    class Meta:
        model = Comments
        fields = ['body']


class BlogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для блогов
    """

    class Meta:
        model = Blogs
        fields = ['id', 'title', 'description', 'created_at', 'updated_at',
                  'owner', 'authors']


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тэгов
    """

    class Meta:
        model = Tags
        fields = ['id', 'title']


class PostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для постов
    """

    class Meta:
        model = Posts
        fields = ['id', 'author', 'title', 'body', 'is_published',
                  'created_at',
                  'likes', 'views', 'blog', 'tags']


class CommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментариев
    """

    class Meta:
        model = Comments
        fields = ['id', 'author', 'body', 'created_at', 'post']
