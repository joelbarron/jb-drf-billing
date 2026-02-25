from django.apps import apps
from django.conf import settings

from .exceptions import BillingConfigurationError

DEFAULTS = {
    "APP_SLUG": None,
    "SCOPE_MODE": "HYBRID",  # USER | PROFILE | HYBRID
    "API_BASE_PATH": "/billing",
    "CATALOG_SOURCE": "DB",  # DB | SETTINGS
    "ENABLE_REVENUECAT": False,
    "ENABLE_STRIPE": False,
    "ENABLE_WEBHOOKS": True,
    "DEFAULT_GRANT_PRIORITY": 100,
    "ACCESS_CHECK_BATCH_LIMIT": 100,
    "FEATURE_FLAGS": {},
    "PROVIDERS": {
        "revenuecat": {
            "API_KEY": None,
            "WEBHOOK_SECRET": None,
            "API_BASE_URL": "https://api.revenuecat.com",
            "REQUEST_TIMEOUT_SECONDS": 15,
            "WEBHOOK_AUTH_HEADER": "authorization",
        },
        "stripe": {
            "API_KEY": None,
            "WEBHOOK_SECRET": None,
        },
    },
    "WEBHOOKS": {},
    "CATALOG": {"apps": [], "plans": [], "prices": [], "entitlements": [], "plan_entitlements": []},
    # extension points
    "CATALOG_PROVIDER_CLASS": "jb_drf_billing.catalog.db_provider.DBCatalogProvider",
    "ENTITLEMENT_RESOLVER_CLASS": "jb_drf_billing.services.entitlements.EntitlementResolver",
    "ACCESS_POLICY_CLASS": "jb_drf_billing.policies.access.DefaultAccessPolicy",
    "FEATURE_VISIBILITY_POLICY_CLASS": "jb_drf_billing.policies.features.DefaultFeatureVisibilityPolicy",
    "CHECKOUT_METADATA_BUILDER_CLASS": None,
    "REVENUECAT_IDENTITY_RESOLVER_CLASS": None,
    "STRIPE_CUSTOMER_RESOLVER_CLASS": None,
    "WEBHOOK_SIGNATURE_VERIFIER_CLASSES": {},
    "WEBHOOK_EVENT_LISTENERS": (),
    "BILLING_STATUS_SERIALIZER_CLASS": None,
    # models (required in integrator)
    "BILLING_CUSTOMER_MODEL": None,
    "PLAN_MODEL": None,
    "PLAN_PRICE_MODEL": None,
    "SUBSCRIPTION_MODEL": None,
    "ENTITLEMENT_MODEL": None,
    "PLAN_ENTITLEMENT_MODEL": None,
    "ENTITLEMENT_GRANT_MODEL": None,
    "BILLING_EVENT_MODEL": None,
    "CHECKOUT_INTENT_MODEL": None,
    "PROFILE_MODEL": None,
}

PREFIX = "JB_DRF_BILLING_"
ROOT_SETTING = "JB_DRF_BILLING"

MODEL_SETTING_KEYS = (
    "BILLING_CUSTOMER_MODEL",
    "PLAN_MODEL",
    "PLAN_PRICE_MODEL",
    "SUBSCRIPTION_MODEL",
    "ENTITLEMENT_MODEL",
    "PLAN_ENTITLEMENT_MODEL",
    "ENTITLEMENT_GRANT_MODEL",
    "BILLING_EVENT_MODEL",
    "CHECKOUT_INTENT_MODEL",
    "PROFILE_MODEL",
)


def get_setting(name: str):
    root = getattr(settings, ROOT_SETTING, None)
    if isinstance(root, dict) and name in root:
        return root[name]
    prefixed = f"{PREFIX}{name}"
    if hasattr(settings, prefixed):
        return getattr(settings, prefixed)
    if hasattr(settings, name):
        return getattr(settings, name)
    return DEFAULTS.get(name)


def get_providers_settings() -> dict:
    defaults = DEFAULTS["PROVIDERS"]
    configured = get_setting("PROVIDERS")
    if not isinstance(configured, dict):
        return defaults
    merged = {**defaults}
    for key in ("revenuecat", "stripe"):
        base_cfg = defaults.get(key, {})
        custom_cfg = configured.get(key, {})
        if isinstance(base_cfg, dict) and isinstance(custom_cfg, dict):
            merged[key] = {**base_cfg, **custom_cfg}
        elif key in configured:
            merged[key] = configured[key]
    for key, value in configured.items():
        if key not in merged:
            merged[key] = value
    return merged


def resolve_model(setting_key: str, required: bool = True):
    dotted = get_setting(setting_key)
    if not dotted:
        if required:
            raise BillingConfigurationError(f"JB_DRF_BILLING['{setting_key}'] is required.")
        return None
    if not isinstance(dotted, str) or "." not in dotted:
        raise BillingConfigurationError(f"JB_DRF_BILLING['{setting_key}'] must be 'app_label.ModelName'.")
    try:
        return apps.get_model(dotted, require_ready=True)
    except Exception as exc:  # pragma: no cover
        raise BillingConfigurationError(
            f"Unable to resolve model for JB_DRF_BILLING['{setting_key}']={dotted!r}."
        ) from exc


def get_app_slug() -> str | None:
    return get_setting("APP_SLUG")


def get_scope_mode() -> str:
    return str(get_setting("SCOPE_MODE") or "HYBRID").upper()
