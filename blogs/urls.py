from django.urls import path

from blogs import views

urlpatterns = [
    path('', views.ListBlogView.as_view(), name='list-of-blogs'),
    path('<int:pk>', views.RetrieveBlogView.as_view(), name='blog-details'),
    path('me/create', views.CreateBlogView.as_view(), name='create-blog'),
    path('me/update/<int:pk>', views.UpdateBlogView.as_view(),
         name='update-blog'),
    path('me/<int:pk>', views.DestroyBlogView.as_view(), name='delete-blog'),
    path('me/add-authors/<int:pk>', views.AddAuthorsToBlogView.as_view(),
         name='add-authors-to-blog'),
    path('publish-post/<int:pk>', views.PublishPostView.as_view(),
         name='publish-post-to-blog'),
    path('subscribe/<int:pk>', views.SubscribeToBlogView.as_view(),
         name='subscribe-to-blog'),
    path('favorites', views.ListFavoriteBlogsView.as_view(),
         name='my-favorite-blogs'),
    path('posts/<int:pk>', views.ListPostsOfBlogView.as_view(),
         name='posts-of-blog'),

    path('posts', views.ListPostsView.as_view(), name='list-of-posts'),
    path('me/post', views.ListUserPostsView.as_view(),
         name='my-posts'),
    path('post/add-comment/<int:pk>',
         views.CreateCommentView.as_view(), name='create-comment-to-post'),
    path('post/add-like/<int:pk>',
         views.LikePostView.as_view(), name='like-post'),
]
