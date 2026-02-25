from django.core import checks
from django.test import SimpleTestCase, override_settings


class BillingChecksTests(SimpleTestCase):
    @override_settings(JB_DRF_BILLING={"APP_SLUG": "x"})
    def test_missing_models_reported(self):
        issues = checks.run_checks()
        self.assertTrue(any(i.id == "jb_drf_billing.E003" for i in issues))
