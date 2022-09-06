from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def create_user(**params):
    return get_user_model().objects.create_common_user(**params)


common_payload = {
    'username': 'testuser2',
    'password': 'testpassword525529!'
}

created_user_payload = {
    'username': 'testuser1',
    'password': 'testpassword525529!'
}

account_create_url = reverse('account-create')
login_url = reverse('login')
blacklist_url = reverse('logout')
token_refresh_url = reverse('token-refresh')


class UserTests(APITestCase):

    def setUp(self) -> None:

        create_user(**created_user_payload)

    def test_create_valid_user(self):
        """Тестирование успешного создания пользователя"""

        url = reverse('account-create')
        response = self.client.post(url, common_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(
            username=common_payload['username'])
        self.assertTrue(user.check_password(common_payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Тестирование создания уже существующего пользователя"""

        url = reverse('account-create')
        response = self.client.post(url, created_user_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_password(self):
        """Тестирование невалидного пароля при создании пользователя"""

        payload = {
            'username': 'testuser3',
            'password': '123'
        }

        url = reverse('account-create')
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            username=payload['username']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Тестирование авторизации пользователя"""

        response = self.client.post(login_url, created_user_payload)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_no_user(self):
        """Тестирование неудачной авторизации пользователя"""

        payload = {
            'username': 'testuser2',
            'password': 'testpass!'
        }

        response = self.client.post(login_url, payload)

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        """
        Тестирование неудачной авторизации,
        из-за неверно заполненых учетных данных
        """
        response = self.client.post(login_url,
                                    {'email': 'one', 'password': ''})

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token(self):
        """Тестирование получения access токена при помощи refresh токена"""

        response_login = self.client.post(login_url, created_user_payload)

        payload = {'refresh': response_login.data['refresh']}

        response = self.client.post(token_refresh_url, payload)
        self.assertIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_invalid_token(self):
        """Тестирование неудачного обновления токена"""

        payload = {'refresh': '123'}

        response = self.client.post(token_refresh_url, payload)
        self.assertNotIn('access', response.data)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['code'], 'token_not_valid')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklist_invalid_token(self):
        """Тестирование неудачного помещения токена в blacklist"""

        payload = {'refresh': '123'}

        response = self.client.post(token_refresh_url, payload)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['code'], 'token_not_valid')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklist_token(self):
        """Тестирование удачного помещения токена в blacklist"""

        response_login = self.client.post(login_url, created_user_payload)

        payload = {'refresh': response_login.data['refresh']}

        response = self.client.post(token_refresh_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
