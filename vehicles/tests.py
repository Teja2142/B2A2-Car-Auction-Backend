from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from dealers.models import DealerProfile
from vehicles.models import Vehicle
from rest_framework_simplejwt.tokens import RefreshToken
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class VehicleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dealeruser', email='dealer@example.com', password='testpass123', mobile='1234567890'
        )
        self.dealer = DealerProfile.objects.create(
            user=self.user,
            company_name='Test Dealer',
            address='123 Main St',
            city='Testville',
            state='TS',
            country='Testland',
            phone='555-1234',
        )
        self.token = str(RefreshToken.for_user(self.user).access_token)
        self.vehicle_url = '/api/vehicles/vehicles/'
        self.vehicle = Vehicle.objects.create(
            vin='1HGCM82633A004352',
            make='Honda',
            model='Accord',
            year=2020,
            color='Blue',
            mileage=10000,
            features='Sunroof, Leather seats',
            description='A well-maintained car',
            transmission='automatic',
            fuel_type='petrol',
            body_style='sedan',
            registration_number='ABC1234',
            dealer=self.dealer,
            starting_price=10000
        )

    def test_vehicle_list(self):
        response = self.client.get(self.vehicle_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_detail(self):
        response = self.client.get(f'{self.vehicle_url}{self.vehicle.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'vin': '2HGCM82633A004353',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2021,
            'color': 'Red',
            'mileage': 5000,
            'features': 'Bluetooth',
            'description': 'Like new',
            'transmission': 'automatic',
            'fuel_type': 'petrol',
            'body_style': 'sedan',
            'registration_number': 'XYZ9876',
            'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_vehicle_update(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.patch(f'{self.vehicle_url}{self.vehicle.id}/', {'color': 'Black'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['color'], 'Black')

    def test_vehicle_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.delete(f'{self.vehicle_url}{self.vehicle.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_vehicle_create_missing_vin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'color': 'Red',
            'mileage': 5000, 'features': 'Bluetooth', 'description': 'Like new',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_style': 'sedan',
            'registration_number': 'NO_VIN', 'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vehicle_create_invalid_year(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'vin': '3HGCM82633A004354', 'make': 'Toyota', 'model': 'Camry', 'year': 1800, 'color': 'Red',
            'mileage': 5000, 'features': 'Bluetooth', 'description': 'Like new',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_style': 'sedan',
            'registration_number': 'BADYEAR', 'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vehicle_create_negative_mileage(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'vin': '4HGCM82633A004355', 'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'color': 'Red',
            'mileage': -100, 'features': 'Bluetooth', 'description': 'Like new',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_style': 'sedan',
            'registration_number': 'NEGMILES', 'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vehicle_create_duplicate_vin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'vin': self.vehicle.vin, 'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'color': 'Red',
            'mileage': 5000, 'features': 'Bluetooth', 'description': 'Like new',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_style': 'sedan',
            'registration_number': 'DUPVIN', 'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vehicle_create_unauthenticated(self):
        data = {
            'vin': '5HGCM82633A004356', 'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'color': 'Red',
            'mileage': 5000, 'features': 'Bluetooth', 'description': 'Like new',
            'transmission': 'automatic', 'fuel_type': 'petrol', 'body_style': 'sedan',
            'registration_number': 'NOAUTH', 'starting_price': 12000
        }
        response = self.client.post(self.vehicle_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_vehicle_filtering(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(f'{self.vehicle_url}?make=Honda')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_ordering(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(f'{self.vehicle_url}?ordering=-year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_search(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(f'{self.vehicle_url}?search=Accord')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cross_dealer_update_delete(self):
        # Create another dealer and vehicle
        other_user = User.objects.create_user(username='other', email='other@example.com', password='testpass123', mobile='2222222222')
        other_dealer = DealerProfile.objects.create(user=other_user, company_name='Other Dealer', address='456 St', city='Otherville', state='OS', country='Otherland', phone='555-2222')
        other_vehicle = Vehicle.objects.create(vin='9HGCM82633A004357', make='Nissan', model='Altima', year=2022, color='Black', mileage=2000, features='', description='', transmission='automatic', fuel_type='petrol', body_style='sedan', registration_number='ALT2022', dealer=other_dealer, starting_price=15000)
        # Try to update/delete as self.user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        update_resp = self.client.patch(f'{self.vehicle_url}{other_vehicle.id}/', {'color': 'Pink'})
        delete_resp = self.client.delete(f'{self.vehicle_url}{other_vehicle.id}/')
        self.assertEqual(update_resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(delete_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_vehicle_image_upload_invalid_type(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        from django.core.files.uploadedfile import SimpleUploadedFile
        invalid_file = SimpleUploadedFile('test.txt', b'notanimage', content_type='text/plain')
        url = '/api/vehicles/vehicleimages/'
        data = {'vehicle': self.vehicle.id, 'image': invalid_file}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE])

    def test_vehicle_image_upload_large_file(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        from django.core.files.uploadedfile import SimpleUploadedFile
        large_content = b'a' * (10 * 1024 * 1024)  # 10MB
        large_file = SimpleUploadedFile('large.jpg', large_content, content_type='image/jpeg')
        url = '/api/vehicles/vehicleimages/'
        data = {'vehicle': self.vehicle.id, 'image': large_file}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
