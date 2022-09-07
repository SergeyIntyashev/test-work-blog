from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserTests(APITestCase):

    def setUp(self) -> None:
        self.account_create_url = reverse('account-create')
        self.login_url = reverse('login')
        self.blacklist_url = reverse('logout')
        self.token_refresh_url = reverse('token-refresh')

        self.testuser_payload = {
            'username': 'testuser1',
            'password': 'testpassword123876521!'
        }

        get_user_model().objects.create_common_user(**self.testuser_payload)

    def test_create_valid_user(self):
        """Тестирование успешного создания пользователя"""

        payload = {
            'username': 'testuser2',
            'password': 'testpassword525529!'
        }

        url = reverse('account-create')
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(
            username=payload['username'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """Тестирование создания пользователя c существующим username"""

        payload = {
            'username': 'testuser1',
            'password': 'testpassword123876521!'
        }

        url = reverse('account-create')
        response = self.client.post(url, payload)

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

        response = self.client.post(self.login_url, self.testuser_payload)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_no_user(self):
        """Тестирование неудачной авторизации пользователя"""

        payload = {
            'username': 'testuser2',
            'password': 'testpass!'
        }

        response = self.client.post(self.login_url, payload)

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        """
        Тестирование неудачной авторизации,
        из-за неверно заполненых учетных данных
        """
        response = self.client.post(self.login_url,
                                    {'email': 'one', 'password': ''})

        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token(self):
        """Тестирование получения access токена при помощи refresh токена"""

        response_login = self.client.post(self.login_url,
                                          self.testuser_payload)

        payload = {'refresh': response_login.data['refresh']}

        response = self.client.post(self.token_refresh_url, payload)
        self.assertIn('access', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_invalid_token(self):
        """Тестирование неудачного обновления токена"""

        payload = {'refresh': '123'}

        response = self.client.post(self.token_refresh_url, payload)
        self.assertNotIn('access', response.data)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['code'], 'token_not_valid')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklist_invalid_token(self):
        """Тестирование неудачного помещения токена в blacklist"""

        payload = {'refresh': '123'}

        response = self.client.post(self.token_refresh_url, payload)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['code'], 'token_not_valid')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_blacklist_token(self):
        """Тестирование удачного помещения токена в blacklist"""

        response_login = self.client.post(self.login_url,
                                          self.testuser_payload)

        payload = {'refresh': response_login.data['refresh']}

        response = self.client.post(self.token_refresh_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
