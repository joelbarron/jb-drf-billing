# TODO[phase-4-stripe]: This service currently delegates to a stub Stripe
# adapter that returns sentinel URLs. When the real adapter ships, the
# response shape (ok, checkoutUrl, sessionId) stays — only the adapter
# methods change. See PHASE_4_TODO.md for the full plan.
from django.apps import apps
from django.db import transaction

from jb_drf_billing.adapters.stripe import StripeBillingAdapter
from jb_drf_billing.conf import get_app_slug, get_setting, resolve_model
from jb_drf_billing.signals import billing_checkout_created


def _resolve_profile_for_user(profile_id, user):
    if not profile_id:
        return None
    profile_model_label = get_setting("PROFILE_MODEL")
    if not profile_model_label:
        return None
    Profile = apps.get_model(profile_model_label)
    return Profile.objects.filter(id=profile_id, user=user).first()


def _record_intent(*, user, billing_customer, plan_price, scope_type, profile, success_url, cancel_url, provider_session_id=None, metadata=None):
    CheckoutIntent = resolve_model("CHECKOUT_INTENT_MODEL")
    intent = CheckoutIntent.objects.create(
        billing_customer=billing_customer,
        app_slug=getattr(plan_price.plan.app, "slug", None) or get_app_slug() or "",
        plan_price=plan_price,
        scope_type=scope_type,
        user=user if scope_type == "USER" else user,
        profile=profile if scope_type == "PROFILE" else None,
        provider="STRIPE",
        status="created",
        success_url=success_url,
        cancel_url=cancel_url,
        provider_session_id=provider_session_id,
        metadata=metadata or {},
    )
    billing_checkout_created.send(sender=_record_intent, intent=intent, user=user)
    return intent


@transaction.atomic
def create_checkout_session(*, user, payload):
    PlanPrice = resolve_model("PLAN_PRICE_MODEL")
    BillingCustomer = resolve_model("BILLING_CUSTOMER_MODEL")

    plan_price = PlanPrice.objects.select_related("plan", "plan__app").filter(id=payload["planPriceId"], is_active=True).first()
    if not plan_price:
        return {"ok": False, "message": "Plan price not found or inactive."}

    scope_type = payload.get("scopeType", "USER")
    profile = _resolve_profile_for_user(payload.get("profileId"), user) if scope_type == "PROFILE" else None
    if scope_type == "PROFILE" and profile is None:
        return {"ok": False, "message": "Profile not found or not owned by user."}

    billing_customer, _ = BillingCustomer.objects.get_or_create(user=user, defaults={"provider_customer_ids": {}})

    adapter = StripeBillingAdapter()
    session = adapter.create_checkout_session(
        user=user,
        plan_price=plan_price,
        scope_type=scope_type,
        profile=profile,
        success_url=payload["successUrl"],
        cancel_url=payload["cancelUrl"],
        metadata={
            "appSlug": getattr(plan_price.plan.app, "slug", None),
            "planPriceId": plan_price.id,
            "userId": getattr(user, "id", None),
            "profileId": getattr(profile, "id", None) if profile else None,
            "scopeType": scope_type,
        },
    )

    intent = _record_intent(
        user=user,
        billing_customer=billing_customer,
        plan_price=plan_price,
        scope_type=scope_type,
        profile=profile,
        success_url=payload["successUrl"],
        cancel_url=payload["cancelUrl"],
        provider_session_id=session.get("sessionId"),
        metadata={"providerResponse": session},
    )

    return {
        "ok": bool(session.get("ok", False)),
        "provider": "stripe",
        "configured": session.get("configured", False),
        "checkoutUrl": session.get("checkoutUrl"),
        "sessionId": session.get("sessionId"),
        "intentId": intent.id,
        "message": session.get("message"),
    }


def create_portal_session(*, user):
    adapter = StripeBillingAdapter()
    return adapter.create_portal_session(user=user)
