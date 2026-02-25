from django.apps import apps

from jb_drf_billing.conf import get_app_slug, get_scope_mode, get_setting, resolve_model
from jb_drf_billing.services.entitlements import EntitlementResolver


def get_billing_status(*, user, app_slug=None):
    slug = app_slug or get_app_slug()
    Subscription = resolve_model("SUBSCRIPTION_MODEL")
    BillingCustomer = resolve_model("BILLING_CUSTOMER_MODEL")
    billing_customer = BillingCustomer.objects.filter(user=user).first()
    active_subscription = None
    if billing_customer:
        active_subscription = (
            Subscription.objects.filter(billing_customer=billing_customer, plan__app__slug=slug)
            .exclude(status__in=["expired"])
            .order_by("-modified")
            .first()
        )

    user_grants = EntitlementResolver.effective_grants_for_user(user, app_slug=slug).select_related("entitlement").order_by("-priority", "-id")
    entitlements_user = []
    seen = set()
    for g in user_grants:
        if g.entitlement.key in seen:
            continue
        seen.add(g.entitlement.key)
        entitlements_user.append({"key": g.entitlement.key, "name": g.entitlement.name, "source": g.source_type})

    profiles_summary = []
    if get_scope_mode() in {"PROFILE", "HYBRID"} and get_setting("PROFILE_MODEL"):
        Profile = apps.get_model(get_setting("PROFILE_MODEL"))
        for p in Profile.objects.filter(user=user, is_active=True)[:50]:
            keys = []
            seen_profile = set()
            for g in EntitlementResolver.effective_grants_for_profile(p, app_slug=slug).select_related("entitlement").order_by("-priority", "-id"):
                if g.entitlement.key in seen_profile:
                    continue
                seen_profile.add(g.entitlement.key)
                keys.append(g.entitlement.key)
            profiles_summary.append({"profileId": p.id, "label": getattr(p, "label", "") or getattr(p, "display_name", ""), "entitlements": keys})

    return {
        "appSlug": slug,
        "subscription": None if not active_subscription else {
            "id": active_subscription.id,
            "status": active_subscription.status,
            "provider": active_subscription.provider,
            "planSlug": active_subscription.plan.slug,
            "planPriceId": active_subscription.plan_price_id,
            "currentPeriodStart": active_subscription.current_period_start,
            "currentPeriodEnd": active_subscription.current_period_end,
            "cancelAtPeriodEnd": active_subscription.cancel_at_period_end,
            "environment": active_subscription.environment,
        },
        "entitlements": {"user": entitlements_user, "profiles": profiles_summary},
        "purchaseChannels": {"ios": ["iap"], "android": ["iap", "web"], "web": ["web"]},
    }
