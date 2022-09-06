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
    path('me/add-authors/<int:pk>', views.AddAuthorsToBlogView.as_view(),
         name='add-authors-to-blog'),
    path('subscribe/<int:pk>', views.SubscribeToBlogView.as_view(),
         name='subscribe-to-blog'),
    path('favorites', views.ListFavoriteBlogsView.as_view(),
         name='my-favorite-blogs'),

    path('posts/<int:pk>', views.ListPostsOfBlogView.as_view(),
         name='posts-of-blog'),
    path('posts', post_actions.list, name='list-of-posts'),
    path('post/<int:pk>', post_actions.retrieve, name='post-details'),
    path('me/posts', views.ListUserPostsView.as_view(), name='my-posts'),
    path('me/post/create/<int:pk>', post_actions.create, name='create-post'),
    path('me/post/update/<int:pk>', post_actions.update, name='update-blog'),
    path('me/post/<int:pk>', post_actions.delete, name='delete-post'),
    path('post/add-comment/<int:pk>', views.CreateCommentView.as_view(),
         name='create-comment-to-post'),
    path('post/add-like/<int:pk>', views.LikePostView.as_view(),
         name='like-post'),
]

router = SimpleRouter()
router.register(r'comment', views.CommentView, basename='Comment')
router.register(r'tag', views.TagsView, basename='Tag')

urlpatterns += router.urls
