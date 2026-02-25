from jb_drf_billing.adapters.revenuecat import RevenueCatAdapter


def sync_mobile_billing(*, user, platform=None, app_user_id=None):
    adapter = RevenueCatAdapter()
    try:
        return adapter.sync_customer(user=user, app_user_id=app_user_id, platform=platform)
    except Exception as exc:
        return {
            "ok": False,
            "provider": "revenuecat",
            "synced": False,
            "message": str(exc),
            "platform": platform,
            "appUserId": app_user_id,
        }
