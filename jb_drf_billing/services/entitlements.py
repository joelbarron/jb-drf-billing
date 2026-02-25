from django.apps import apps
from django.db import transaction
from django.utils import timezone

from jb_drf_billing.conf import get_app_slug, get_setting, resolve_model
from jb_drf_billing.signals import billing_entitlements_updated


def _active_grants_queryset(grant_model, *, app_slug, scope_type, user=None, profile=None):
    now = timezone.now()
    base = grant_model.objects.select_related("entitlement", "subscription").filter(
        app_slug=app_slug,
        scope_type=scope_type,
        is_active=True,
        starts_at__lte=now,
    )
    if scope_type == "USER":
        base = base.filter(user=user)
    elif scope_type == "PROFILE":
        base = base.filter(profile=profile)
    return base.filter(ends_at__isnull=True) | base.filter(ends_at__gt=now)


class EntitlementResolver:
    @staticmethod
    def effective_grants_for_user(user, *, app_slug=None):
        Grant = resolve_model("ENTITLEMENT_GRANT_MODEL")
        return _active_grants_queryset(Grant, app_slug=app_slug or get_app_slug(), scope_type="USER", user=user)

    @staticmethod
    def effective_grants_for_profile(profile, *, app_slug=None):
        Grant = resolve_model("ENTITLEMENT_GRANT_MODEL")
        return _active_grants_queryset(
            Grant,
            app_slug=app_slug or get_app_slug(),
            scope_type="PROFILE",
            profile=profile,
        )


@transaction.atomic
def replace_subscription_grants(
    *,
    subscription,
    scope_type="USER",
    user=None,
    profile=None,
    app_slug=None,
    source_type="SUBSCRIPTION",
):
    PlanEntitlement = resolve_model("PLAN_ENTITLEMENT_MODEL")
    Grant = resolve_model("ENTITLEMENT_GRANT_MODEL")

    resolved_app_slug = app_slug or getattr(subscription.plan.app, "slug", None) or get_app_slug()
    resolved_user = user or getattr(subscription.billing_customer, "user", None)

    delete_qs = Grant.objects.filter(subscription=subscription)
    if scope_type == "USER":
        delete_qs = delete_qs.filter(user=resolved_user)
    elif scope_type == "PROFILE" and profile is not None:
        delete_qs = delete_qs.filter(profile=profile)
    delete_qs.delete()

    if subscription.status not in {"active", "trialing", "grace_period"}:
        billing_entitlements_updated.send(
            sender=replace_subscription_grants,
            user=resolved_user,
            app_slug=resolved_app_slug,
            subscription=subscription,
            created_count=0,
        )
        return []

    plan_ents = PlanEntitlement.objects.select_related("entitlement").filter(plan=subscription.plan)
    starts_at = subscription.current_period_start or timezone.now()
    ends_at = subscription.current_period_end
    default_priority = int(get_setting("DEFAULT_GRANT_PRIORITY") or 100)

    created = []
    for pe in plan_ents:
        kwargs = {
            "app_slug": resolved_app_slug,
            "scope_type": scope_type,
            "entitlement": pe.entitlement,
            "source_type": source_type,
            "subscription": subscription,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "is_active": True,
            "priority": default_priority,
            "metadata": {
                "quota": pe.quota,
                "flags": pe.flags or {},
                "planEntitlementId": pe.id,
            },
        }
        if scope_type == "USER":
            kwargs["user"] = resolved_user
        else:
            kwargs["user"] = resolved_user
            kwargs["profile"] = profile
        created.append(Grant.objects.create(**kwargs))

    billing_entitlements_updated.send(
        sender=replace_subscription_grants,
        user=resolved_user,
        app_slug=resolved_app_slug,
        subscription=subscription,
        created_count=len(created),
    )
    return created


def list_effective_entitlements(user, *, app_slug=None):
    grants = EntitlementResolver.effective_grants_for_user(user, app_slug=app_slug).order_by("-priority", "-id")
    billing_entitlements_updated.send(sender=list_effective_entitlements, user=user, app_slug=app_slug)
    return list(grants)
