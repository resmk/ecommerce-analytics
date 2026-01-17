
from django.test import TestCase
from django.urls import reverse

from analytics.models import FactOrder


class KPITestCase(TestCase):
    def test_kpis_endpoint_returns_200(self):
        url = "/api/v1/kpis/?date_from=2000-01-01&date_to=2100-01-01"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_revenue", response.json())
        
class CustomerSegmentsTestCase(TestCase):
    def test_customer_segments_returns_200(self):
        url = "/api/v1/customers/segments/?date_from=2000-01-01&date_to=2100-01-01"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("segments", response.json())
        
class TopProductsTestCase(TestCase):
    def test_top_products_returns_200(self):
        url = "/api/v1/products/top-sellers/?metric=revenue&limit=10&date_from=2000-01-01&date_to=2100-01-01"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())

