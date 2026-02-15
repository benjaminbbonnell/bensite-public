from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import Locations
from decimal import Decimal

class LocationListAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/weather/api/locations/"

        test_data = [
            (1, "Washington", "DC", "USA", Decimal("38.9072"), Decimal("-77.0369")),
            (2, "Dallas", "TX", "USA", Decimal("32.7767"), Decimal("-96.797")),
        ]

        Locations.objects.bulk_create([
            Locations(city_id = id, city_name = name, state_code = state, country_code = country, latitude = lat, longitude = lon)
            for id, name, state, country, lat, lon in test_data
        ])

    def test_location_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)        