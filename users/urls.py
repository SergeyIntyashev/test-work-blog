from django.urls import path
from rest_framework_simplejwt.views import token_refresh, \
    token_obtain_pair, token_blacklist

from users.views import CreateCommonUser

urlpatterns = [
    path('sign-in', CreateCommonUser.as_view(), name='account-create'),
    path('login', token_obtain_pair, name='login'),
    path('logout', token_blacklist, name='logout'),
    path('token/refresh', token_refresh, name='token-refresh'),
]
