from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import DealerProfile
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class DealerAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('dealer_register')
        self.login_url = reverse('dealer_login')
        self.profile_url = '/api/dealers/dealer-profiles/'
        self.user = User.objects.create_user(
            username='dealeruser', email='dealer@example.com', password='testpass123', mobile='1234567890'
        )
        self.profile = DealerProfile.objects.create(
            user=self.user,
            company_name='Test Dealer',
            address='123 Main St',
            city='Testville',
            state='TS',
            country='Testland',
            phone='555-1234',
            email='dealer@example.com',
            website='',
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)

    def test_dealer_registration(self):
        data = {
            'username': 'newdealer',
            'email': 'newdealer@example.com',
            'password': 'testpass123',
            'company_name': 'New Dealer',
            'address': '456 Main St',
            'city': 'Newcity',
            'state': 'NS',
            'country': 'Newland',
            'phone': '555-5678',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_dealer_login(self):
        data = {'email': 'dealer@example.com', 'password': 'testpass123'}
        response = self.client.post(self.login_url, data)
        if response.status_code != status.HTTP_200_OK:
            self.fail(f'Dealer login failed: {response.status_code} {response.data}')
        self.assertIn('access', response.data)

    def test_dealer_profile_list(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dealer_profile_update(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.patch(f'{self.profile_url}{self.profile.id}/', {'company_name': 'Updated Dealer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Updated Dealer')

    def test_dealer_registration_duplicate_email(self):
        data = {
            'username': 'anotherdealer',
            'email': 'dealer@example.com',  # duplicate
            'password': 'testpass123',
            'company_name': 'Dup Dealer',
            'address': '789 Main St',
            'city': 'Dupcity',
            'state': 'DS',
            'country': 'Dupland',
            'phone': '555-9999',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dealer_registration_missing_fields(self):
        data = {
            'username': '',
            'email': '',
            'password': '',
            'company_name': '',
            'address': '',
            'city': '',
            'state': '',
            'country': '',
            'phone': '',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dealer_profile_list_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cross_dealer_profile_update_delete(self):
        # Create another dealer
        other_user = User.objects.create_user(username='otherdealer', email='otherdealer@example.com', password='testpass123', mobile='8888888888')
        other_profile = DealerProfile.objects.create(user=other_user, company_name='Other Dealer', address='789 St', city='Otherville', state='OS', country='Otherland', phone='555-8888', email='otherdealer@example.com', website='')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        update_resp = self.client.patch(f'{self.profile_url}{other_profile.id}/', {'company_name': 'Hacked'})
        delete_resp = self.client.delete(f'{self.profile_url}{other_profile.id}/')
        self.assertEqual(update_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_resp.status_code, status.HTTP_403_FORBIDDEN)
