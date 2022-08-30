from django.urls import path

from blogs import views

# router = SimpleRouter()

urlpatterns = [
    path('', views.CreateBlog.as_view(), name='create-blog'),
    path('<int:pk>', views.AddAuthorsToBlog.as_view(),
         name='add-authors-to-blog'),
]
