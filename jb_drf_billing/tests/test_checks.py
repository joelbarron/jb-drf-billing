from django.test import SimpleTestCase, override_settings

from jb_drf_billing.checks import billing_configuration_check


class BillingChecksTests(SimpleTestCase):
    @override_settings(JB_DRF_BILLING={"APP_SLUG": "x"})
    def test_missing_models_reported(self):
        issues = billing_configuration_check(app_configs=None)
        self.assertTrue(any(i.id == "jb_drf_billing.E003" for i in issues))
