from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class UserAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('register_user')
        self.login_url = reverse('login')
        self.jwt_url = reverse('token_obtain_pair')
        self.user_data = {
            'name': 'apitestuser',
            'email': 'apitest@example.com',
            'password': 'testpass123',
            'confirmPassword': 'testpass123',
            'mobile': '1234567890'
        }
        self.user = User.objects.create_user(
            username='apitestuser', email='apitest@example.com', password='testpass123', mobile='1234567890'
        )

    def test_user_registration(self):
        data = self.user_data.copy()
        data['name'] = 'newuser'
        data['email'] = 'newuser@example.com'
        data['mobile'] = '9999999999'
        response = self.client.post(self.register_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_user_login(self):
        response = self.client.post(self.login_url, {'email': 'apitest@example.com', 'password': 'testpass123'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue('token' in response.data or 'access' in response.data)

    def test_jwt_token_auth(self):
        response = self.client.post(self.jwt_url, {'email': 'apitest@example.com', 'password': 'testpass123'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertTrue('token' in response.data or 'access' in response.data)

    def test_password_reset_request(self):
        url = reverse('request_password_reset')
        response = self.client.post(url, {'email': 'apitest@example.com'})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])

    def test_password_reset_confirm(self):
        import uuid
        token = str(uuid.uuid4())
        self.user.reset_token = token
        self.user.save()
        url = reverse('reset_password', kwargs={'token': token})
        response = self.client.post(
            url,
            {'password': 'newpass123', 'confirmPassword': 'newpass123'},
            format='json',
            HTTP_ACCEPT='application/json'
        )
        print('Password reset confirm response:', response.status_code, getattr(response, 'data', response.content))
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])

    def test_password_reset_confirm_invalid_token(self):
        import uuid
        fake_token = str(uuid.uuid4())
        url = reverse('reset_password', kwargs={'token': fake_token})
        response = self.client.post(url, {'password': 'newpass123', 'confirmPassword': 'newpass123'}, format='json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_missing_fields(self):
        import uuid
        token = str(uuid.uuid4())
        self.user.reset_token = token
        self.user.save()
        url = reverse('reset_password', kwargs={'token': token})
        response = self.client.post(url, {'password': 'newpass123'}, format='json', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)
