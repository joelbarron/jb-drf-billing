from django.apps import apps

from jb_drf_billing.conf import get_setting, resolve_model
from jb_drf_billing.policies.access import DefaultAccessPolicy
from jb_drf_billing.services.entitlements import EntitlementResolver


def _resolve_profile_for_user(profile_id, user):
    if not profile_id:
        return None
    profile_model_label = get_setting("PROFILE_MODEL")
    Profile = apps.get_model(profile_model_label)
    return Profile.objects.filter(id=profile_id, user=user).first()


def check_access_batch(*, user, features, scope_type="USER", profile_id=None, app_slug=None):
    if len(features) > int(get_setting("ACCESS_CHECK_BATCH_LIMIT") or 100):
        raise ValueError("Too many features requested in access check batch.")

    policy = DefaultAccessPolicy()
    profile = _resolve_profile_for_user(profile_id, user) if scope_type == "PROFILE" else None
    if not policy.can_check(user, scope_type=scope_type, profile=profile):
        return [{"featureKey": f, "enabled": False, "reason": "forbidden", "source": None} for f in features]

    grants = (
        EntitlementResolver.effective_grants_for_profile(profile, app_slug=app_slug)
        if scope_type == "PROFILE" and profile is not None
        else EntitlementResolver.effective_grants_for_user(user, app_slug=app_slug)
    )
    grant_map = {}
    for grant in grants.order_by("-priority", "-id"):
        key = grant.entitlement.key
        grant_map.setdefault(
            key,
            {
                "featureKey": key,
                "enabled": True,
                "reason": "granted",
                "source": grant.source_type,
                "scopeType": grant.scope_type,
            },
        )

    return [grant_map.get(f, {"featureKey": f, "enabled": False, "reason": "missing_entitlement", "source": None}) for f in features]
