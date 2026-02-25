from django.test import SimpleTestCase, override_settings

from jb_drf_billing.conf import get_setting, get_scope_mode


class BillingConfTests(SimpleTestCase):
    def test_defaults(self):
        self.assertEqual(get_scope_mode(), "HYBRID")

    @override_settings(JB_DRF_BILLING={"APP_SLUG": "finzenio", "SCOPE_MODE": "user"})
    def test_root_settings_override(self):
        self.assertEqual(get_setting("APP_SLUG"), "finzenio")
        self.assertEqual(get_scope_mode(), "USER")
