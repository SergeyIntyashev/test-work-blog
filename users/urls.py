from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import CreateCommonUser, LoginAPIView, LogoutAPIView

urlpatterns = [
    path('users/', CreateCommonUser.as_view(), name='account-create'),
    path('login/', LoginAPIView.as_view(), name='token-login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
