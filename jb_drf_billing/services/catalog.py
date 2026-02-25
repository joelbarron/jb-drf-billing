from jb_drf_billing.catalog.db_provider import DBCatalogProvider
from jb_drf_billing.catalog.settings_provider import SettingsCatalogProvider
from jb_drf_billing.conf import get_setting


def get_catalog_payload(*, user=None, app_slug=None, platform=None, country_code=None, currency=None):
    source = str(get_setting("CATALOG_SOURCE") or "DB").upper()
    provider = SettingsCatalogProvider() if source == "SETTINGS" else DBCatalogProvider()
    return provider.get_catalog(
        user=user,
        app_slug=app_slug,
        platform=platform,
        country_code=country_code,
        currency=currency,
    )
