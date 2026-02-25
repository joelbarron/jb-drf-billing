from jb_drf_billing.catalog.base import BaseCatalogProvider
from jb_drf_billing.conf import get_setting


class SettingsCatalogProvider(BaseCatalogProvider):
    def get_catalog(self, *, user=None, app_slug=None, platform=None, country_code=None, currency=None):
        payload = get_setting("CATALOG") or {}
        return {
            "appSlug": app_slug or get_setting("APP_SLUG"),
            "purchaseChannels": payload.get("purchaseChannels", {"ios": ["iap"], "android": ["iap", "web"], "web": ["web"]}),
            "plans": payload.get("plans", []),
        }
