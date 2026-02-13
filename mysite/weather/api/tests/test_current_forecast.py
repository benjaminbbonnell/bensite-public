from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import ForecastData, Locations
import time
from decimal import Decimal

class CurrentForecastAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/weather/api/currentforecast/"
        
        self.location1 = Locations.objects.create(
            city_id=1,
            city_name="Washington",
            state_code="DC",
            country_code="USA",
            latitude=Decimal("38.9072"),
            longitude=Decimal("-77.0369")
        )
        
        self.location2 = Locations.objects.create(
            city_id=2,
            city_name="Dallas",
            state_code="TX",
            country_code="USA",
            latitude=Decimal("32.7767"),
            longitude=Decimal("-96.7970")
        )
        
        self.current_time = round((int(time.time())) // 3600) * 3600
        
        self.create_forecast_data(
            api_name="openmeteo",
            city_id=1,
            city_name="Washington",
            hours_ahead=0,
            temp=35.0,
            feels_like=27.8
        )
        
        self.create_forecast_data(
            api_name="weathercom",
            city_id=1,
            city_name="Washington",
            hours_ahead=0,
            temp=32.4,
            feels_like=28.4
        )
        
        self.create_forecast_data(
            api_name="openmeteo",
            city_id=1,
            city_name="Washington",
            hours_ahead=6,
            temp=38.2,
            feels_like=30.1
        )
        
        self.create_forecast_data(
            api_name="openmeteo",
            city_id=2,
            city_name="Dallas",
            hours_ahead=0,
            temp=55.0,
            feels_like=50.0
        )
    
    def create_forecast_data(self, api_name, city_id, city_name, hours_ahead, temp, feels_like):
        forecast_epoch = self.current_time + (hours_ahead * 3600)
        ForecastData.objects.create(
            api_name=api_name,
            city_id=city_id,
            city=city_name,
            forecast_made=self.current_time,
            forecast_epoch=forecast_epoch,
            temp_f=Decimal(str(temp)),
            feelslike_f=Decimal(str(feels_like)),
            condition="Clear",
            precip_prob=Decimal("0.0"),
            chance_of_rain=Decimal("0.0"),
            chance_of_snow=Decimal("0.0")
        )
    
    def test_get_current_forecast_with_valid_city_id(self):
        response = self.client.get(self.url, {"city_id": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # Location 1 should be washington DC
        location_data = response.data[0]["location"]
        self.assertEqual(location_data["location_id"], 1)
        self.assertEqual(location_data["name"], "Washington")
        self.assertEqual(location_data["state"], "DC")
        self.assertEqual(location_data["country"], "USA")
        
        forecast_data = response.data[1]
        self.assertIsInstance(forecast_data, dict)
        self.assertTrue(len(forecast_data) > 0)
    
    def test_get_current_forecast_with_valid_lat_lon(self):
        response = self.client.get(self.url, {"lat": 38.9072, "lon": -77.0369})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location_data = response.data[0]["location"]
        self.assertEqual(location_data["location_id"], 1)
        self.assertEqual(location_data["name"], "Washington")
    
    def test_get_current_forecast_haversine_distance_test(self):
        response = self.client.get(self.url, {"lat": 39, "lon": -78})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        location_data = response.data[0]["location"]
        self.assertEqual(location_data["location_id"], 1)
        self.assertEqual(location_data["name"], "Washington")