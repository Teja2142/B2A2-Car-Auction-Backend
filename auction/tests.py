from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Vehicle
import uuid

class VehicleModelTestCase(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            make='Toyota', model='Camry', year=2020, condition='New', max_price=20000.00
        )

    def test_vehicle_str(self):
        self.assertEqual(str(self.vehicle), 'Toyota Camry (2020)')

class VehicleAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vehicle = Vehicle.objects.create(
            make='Honda', model='Civic', year=2021, condition='Used', max_price=15000.00
        )

    def test_vehicle_list(self):
        url = reverse('vehicle-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_vehicle_detail(self):
        url = reverse('vehicle-detail', kwargs={'id': str(self.vehicle.id)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
