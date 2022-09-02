from blogs.models import Posts


def add_like_to_post(post: Posts) -> None:
    """
    Инкрементирует лайки поста
    """
    post.likes += 1
    post.save()
