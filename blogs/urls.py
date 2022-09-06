from django.urls import path
from rest_framework.routers import SimpleRouter

from blogs import views
from blogs.services import get_views_actions_model

blog_actions = get_views_actions_model(views.BlogsView)
post_actions = get_views_actions_model(views.PostsView)

urlpatterns = [
    path('', blog_actions.list, name='list-of-blogs'),
    path('<int:pk>', blog_actions.retrieve, name='blog-details'),
    path('me/create', blog_actions.create, name='create-blog'),
    path('me/update/<int:pk>', blog_actions.update, name='update-blog'),
    path('me/<int:pk>', blog_actions.delete, name='delete-blog'),
    path('me/add-authors/<int:pk>', views.add_author_to_blog,
         name='add-authors-to-blog'),
    path('subscribe/<int:pk>', views.subscribe_to_blog,
         name='subscribe-to-blog'),
    path('favorites', views.favorites_blogs, name='my-favorite-blogs'),

    path('posts/<int:pk>', views.blog_posts, name='posts-of-blog'),
    path('posts', post_actions.list, name='list-of-posts'),
    path('post/<int:pk>', post_actions.retrieve, name='post-details'),
    path('me/posts', views.user_posts, name='my-posts'),
    path('me/post/create/<int:pk>', post_actions.create, name='create-post'),
    path('me/post/update/<int:pk>', post_actions.update, name='update-blog'),
    path('me/post/<int:pk>', post_actions.delete, name='delete-post'),
    path('post/add-comment/<int:pk>', views.create_comment,
         name='create-comment-to-post'),
    path('post/add-like/<int:pk>', views.like_post, name='like-post'),
]

router = SimpleRouter()
router.register(r'comment', views.CommentView, basename='Comment')
router.register(r'tag', views.TagsView, basename='Tag')

urlpatterns += router.urls
