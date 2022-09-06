from django.urls import path
from rest_framework.routers import SimpleRouter

from blogs import views

urlpatterns = [
    path('blogs/<int:pk>/add-authors', views.AddAuthorsToBlogView.as_view(),
         name='add-authors-to-blog'),
    path('blogs/<int:pk>/subscribe', views.SubscribeToBlogView.as_view(),
         name='subscribe-to-blog'),
    path('blogs/<int:pk>/posts', views.ListPostsOfBlogView.as_view(),
         name='posts-of-blog'),
    path('blogs/favorites', views.ListFavoriteBlogsView.as_view(),
         name='my-favorite-blogs'),
    path('posts/my', views.ListUserPostsView.as_view(), name='my-posts'),
    path('posts/<int:pk>/add-comment', views.CreateCommentView.as_view(),
         name='create-comment-to-post'),
    path('posts/<int:pk>/add-like', views.LikePostView.as_view(),
         name='like-post'),
]

router = SimpleRouter()
router.register(r'comments', views.CommentView, basename='Comments')
router.register(r'tags', views.TagsView, basename='Tags')
router.register(r'blogs', views.BlogsView, basename='Blogs')
router.register(r'posts', views.PostsView, basename='Posts')

urlpatterns += router.urls
