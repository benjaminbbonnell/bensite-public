from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from weather.models import MonthlyAverageChart
from decimal import Decimal

class MonthlyAveragesAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/weather/api/ma/"

        test_data = [
            ("openmeteo", 1, 0.77, 1),
            ("openmeteo", 1, 1.09, 6),
            ("openmeteo", 1, 1.58, 12),
            ("openmeteo", 1, 1.69, 24),
            ("tomorrowio", 1, 0.77, 1),
            ("tomorrowio", 1, 1.22, 6),
            ("tomorrowio", 1, 2.42, 12),
            ("tomorrowio", 1, 2.76, 24),
            ("openmeteo", 2, 0.74, 1),
            ("openmeteo", 2, 1.04, 6),
            ("openmeteo", 2, 1.54, 12),
            ("openmeteo", 2, 1.64, 24),
            ("tomorrowio", 2, 0.94, 1),
            ("tomorrowio", 2, 1.24, 6),
            ("tomorrowio", 2, 2.44, 12),
            ("tomorrowio", 2, 2.74, 24),
        ]

        MonthlyAverageChart.objects.bulk_create([
            MonthlyAverageChart(api_name=api, month=mon, avg_dif=avg, hoursbefore=hours)
            for api, mon, avg, hours in test_data
        ])

#params - hoursbefore, month, api_name
    def test_monthly_average_chart(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)
    
    def test_monthly_average_chart_month_param(self):
        response = self.client.get(self.url, {"month": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data[0]

        self.assertEqual(response_data["months"]["January"][1], Decimal("0.77"))

    def test_monthly_average_chart_api_param(self):
        response = self.client.get(self.url, {"api_name": "tomorrowio"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data[0]

        self.assertEqual(response_data["api_name"], "tomorrowio")

    def test_monthly_average_chart_hours_before_param(self):
        response = self.client.get(self.url, {"api_name": "tomorrowio", "hoursbefore": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data[0]

        self.assertEqual(response_data["months"]["January"][1], Decimal("0.77"))
        self.assertEqual(response_data["months"]["January"][6], Decimal("1.22"))

        self.assertTrue(all(key <= 6 for key in response_data["months"]["January"].keys()))

