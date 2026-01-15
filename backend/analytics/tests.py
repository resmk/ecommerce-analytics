
from django.test import TestCase
from django.urls import reverse

from analytics.models import FactOrder


class KPITestCase(TestCase):
    def test_kpis_endpoint_returns_200(self):
        url = "/api/v1/kpis/?date_from=2000-01-01&date_to=2100-01-01"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_revenue", response.json())
