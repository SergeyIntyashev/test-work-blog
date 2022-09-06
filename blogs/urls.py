from django.urls import path
from rest_framework.routers import SimpleRouter

from blogs import views

blog_list = views.BlogsView.as_view({
    'get': 'list',
})

blog_create = views.BlogsView.as_view({
    'post': 'create',
})

blog_detail = views.BlogsView.as_view({
    'get': 'retrieve',
})

blog_update = views.BlogsView.as_view({
    'put': 'update',
    'patch': 'partial_update',
})

blog_delete = views.BlogsView.as_view({
    'delete': 'destroy'
})

urlpatterns = [
    path('', blog_list, name='list-of-blogs'),
    path('<int:pk>', blog_detail, name='blog-details'),
    path('me/create', blog_create, name='create-blog'),
    path('me/update/<int:pk>', blog_update,
         name='update-blog'),
    path('me/<int:pk>', blog_delete,
         name='delete-blog'),
    path('me/add-authors/<int:pk>', views.AddAuthorsToBlogView.as_view(),
         name='add-authors-to-blog'),
    path('subscribe/<int:pk>', views.SubscribeToBlogView.as_view(),
         name='subscribe-to-blog'),
    path('favorites', views.ListFavoriteBlogsView.as_view(),
         name='my-favorite-blogs'),

    path('posts/<int:pk>', views.ListPostsOfBlogView.as_view(),
         name='posts-of-blog'),
    path('posts', views.ListPostsView.as_view(), name='list-of-posts'),
    path('post/<int:pk>', views.RetrievePostView.as_view(),
         name='post-details'),
    path('me/posts', views.ListUserPostsView.as_view(),
         name='my-posts'),
    path('me/post/create/<int:pk>', views.CreatePostView.as_view(),
         name='create-post'),
    path('me/post/update/<int:pk>', views.UpdateDestroyPostView.as_view(),
         name='update-blog'),
    path('me/post/<int:pk>', views.UpdateDestroyPostView.as_view(),
         name='delete-post'),
    path('post/add-comment/<int:pk>',
         views.CreateCommentView.as_view(), name='create-comment-to-post'),
    path('post/add-like/<int:pk>',
         views.LikePostView.as_view(), name='like-post'),
]

router = SimpleRouter()
router.register(r'comment', views.CommentView, basename='Comment')
router.register(r'tag', views.TagsView, basename='Tag')

urlpatterns += router.urls
