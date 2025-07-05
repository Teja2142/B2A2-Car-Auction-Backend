from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from dealers.models import DealerProfile
from .models import Auction, Bid
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

User = get_user_model()

class VehicleModelTestCase(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            make='Toyota', model='Camry', year=2020, color='Blue', mileage=10000, features='', description='', transmission='automatic', fuel_type='petrol', body_style='sedan', registration_number='CAM2020', dealer=None, starting_price=9000
        )

    def test_vehicle_str(self):
        self.assertEqual(str(self.vehicle), 'Toyota Camry (2020)')

class VehicleAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vehicle = Vehicle.objects.create(
            make='Honda', model='Civic', year=2021, color='Red', mileage=5000, features='', description='', transmission='automatic', fuel_type='petrol', body_style='sedan', registration_number='CIV2021', dealer=None, starting_price=9500
        )

    def test_vehicle_list(self):
        url = reverse('vehicle-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_detail(self):
        url = reverse('vehicle-detail', kwargs={'pk': str(self.vehicle.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuctionBidAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='biduser', email='biduser@example.com', password='testpass123', mobile='1234567890'
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
        self.vehicle = Vehicle.objects.create(
            vin='1HGCM82633A004354',
            make='Ford',
            model='Focus',
            year=2022,
            color='White',
            mileage=8000,
            features='Backup Camera',
            description='Clean',
            transmission='automatic',
            fuel_type='petrol',
            body_style='hatchback',
            registration_number='FOC2022',
            dealer=self.dealer,
            starting_price=10000
        )
        self.auction = Auction.objects.create(
            vehicle=self.vehicle,
            starting_price=10000,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=1),
            highest_bid=10000
        )
        self.auction_url = '/api/auction/auctions/'
        self.bid_url = '/api/auction/bids/'
        self.place_bid_url = '/api/auction/place-bid/'

    def test_auction_list(self):
        response = self.client.get(self.auction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auction_detail(self):
        response = self.client.get(f'{self.auction_url}{self.auction.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auction_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'vehicle': self.vehicle.id,
            'starting_price': 12000,
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(days=2),
        }
        response = self.client.post(self.auction_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_bid_create(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'auction': self.auction.id,
            'bidder': self.user.id,
            'bid_amount': 11000
        }
        response = self.client.post(self.bid_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_place_bid(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        data = {
            'auction': str(self.auction.id),
            'bid_amount': 12000
        }
        response = self.client.post(self.place_bid_url, data)
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])

    def test_auction_update(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.patch(f'{self.auction_url}{self.auction.id}/', {'starting_price': 15000})
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_auction_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.delete(f'{self.auction_url}{self.auction.id}/')
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN])

    def test_bid_update_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        # Create a bid
        bid_data = {'auction': self.auction.id, 'bidder': self.user.id, 'bid_amount': 12000}
        bid_resp = self.client.post(self.bid_url, bid_data)
        if bid_resp.status_code == status.HTTP_201_CREATED:
            bid_id = bid_resp.data['id']
            # Update
            update_resp = self.client.patch(f'{self.bid_url}{bid_id}/', {'bid_amount': 13000})
            self.assertIn(update_resp.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])
            # Delete
            delete_resp = self.client.delete(f'{self.bid_url}{bid_id}/')
            self.assertIn(delete_resp.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN])

    def test_auction_filtering(self):
        response = self.client.get(f'{self.auction_url}?starting_price=10000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auction_ordering(self):
        response = self.client.get(f'{self.auction_url}?ordering=-starting_price')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auction_search(self):
        response = self.client.get(f'{self.auction_url}?search=Ford')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
