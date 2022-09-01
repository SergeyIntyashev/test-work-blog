from django.urls import path

from blogs import views

# router = SimpleRouter()

urlpatterns = [
    path('', views.CreateBlog.as_view(), name='create-blog'),
    path('<int:pk>/add-authors', views.AddAuthorsToBlog.as_view(),
         name='add-authors-to-blog'),
    path('<int:blog_id>/publish-post/', views.PublishPost.as_view(),
         name='publish-post-to-blog'),
    path('<int:blog_id>/add-comment/<int:post_id>',
         views.CreateComment.as_view(), name='create-comment-to-post'),
    path('<int:blog_id>/add-like/<int:post_id>',
         views.LikePost.as_view(), name='like-post')
]
