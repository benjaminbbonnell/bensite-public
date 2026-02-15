from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import HoursBeforeChart
import time
from decimal import Decimal

class HoursBeforeAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/weather/api/hb/"

        test_data = [
            ("openmeteo", 0, 0),
            ("openmeteo", 0.77, 1),
            ("openmeteo", 1.09, 2),
            ("openmeteo", 1.58, 3),
            ("openmeteo", 1.69, 4),
            ("tomorrowio", 0.0, 0),
            ("tomorrowio", 0.93, 1),
            ("tomorrowio", 1.22, 2),
            ("tomorrowio", 2.42, 3),
            ("tomorrowio", 2.76, 4),
        ]

        HoursBeforeChart.objects.bulk_create([
            HoursBeforeChart(api_name=api, avg_dif=avg, hoursbefore=hours)
            for api, avg, hours in test_data
        ])

    def test_hours_before_chart(self):
        response = self.client.get(self.url, {"hoursbefore": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_hours_before_chart_api_param(self):
        response = self.client.get(self.url, {"hoursbefore": 4, "api_name": "openmeteo"})

        response_data_1 = response.data[0]

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response_data_1["api_name"], "openmeteo")
        self.assertEqual(response_data_1["hours_before"][0], 0)
        self.assertEqual(response_data_1["hours_before"][1], Decimal("0.77"))

    def test_hours_before_chart_hours_before_param(self):
        response = self.client.get(self.url, {"hoursbefore": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response_data_1 = response.data[0]
        self.assertEqual(len(response_data_1["hours_before"]), 3)


