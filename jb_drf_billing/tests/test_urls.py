from django.urls import resolve
from django.test import SimpleTestCase


class BillingUrlsTests(SimpleTestCase):
    def test_catalog_url_resolves(self):
        self.assertEqual(resolve("/catalog").view_name, "billing-catalog")
