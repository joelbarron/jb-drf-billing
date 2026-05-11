from django.core.checks import Error, Warning, register

from jb_drf_billing.conf import get_providers_settings, get_scope_mode, get_setting


@register()
def billing_configuration_check(app_configs, **kwargs):
    issues = []
    app_slug = get_setting("APP_SLUG")
    if not app_slug:
        issues.append(Error("Missing JB_DRF_BILLING['APP_SLUG'].", id="jb_drf_billing.E001"))

    scope_mode = get_scope_mode()
    if scope_mode not in {"USER", "PROFILE", "HYBRID"}:
        issues.append(Error("JB_DRF_BILLING['SCOPE_MODE'] must be USER, PROFILE, or HYBRID.", id="jb_drf_billing.E002"))

    required_models = [
        "BILLING_CUSTOMER_MODEL",
        "PLAN_MODEL",
        "PLAN_PRICE_MODEL",
        "SUBSCRIPTION_MODEL",
        "ENTITLEMENT_MODEL",
        "PLAN_ENTITLEMENT_MODEL",
        "ENTITLEMENT_GRANT_MODEL",
        "BILLING_EVENT_MODEL",
        "CHECKOUT_INTENT_MODEL",
    ]
    if scope_mode in {"PROFILE", "HYBRID"}:
        required_models.append("PROFILE_MODEL")

    for key in required_models:
        if not get_setting(key):
            issues.append(Error(f"Missing JB_DRF_BILLING['{key}'].", id="jb_drf_billing.E003"))

    providers = get_providers_settings()
    if get_setting("ENABLE_STRIPE") and not (providers.get("stripe") or {}).get("WEBHOOK_SECRET"):
        issues.append(Warning("Stripe enabled without webhook secret.", id="jb_drf_billing.W001"))
    if get_setting("ENABLE_REVENUECAT") and not (providers.get("revenuecat") or {}).get("WEBHOOK_SECRET"):
        issues.append(Warning("RevenueCat enabled without webhook secret.", id="jb_drf_billing.W002"))

    return issues
