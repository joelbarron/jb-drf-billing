from jb_drf_billing.adapters.revenuecat import RevenueCatAdapter


def process_revenuecat_webhook(payload, headers=None):
    adapter = RevenueCatAdapter()
    return adapter.process_webhook(payload or {}, headers=headers)


def process_stripe_webhook(payload, headers=None):
    return {"ok": True, "processed": False, "provider": "stripe", "message": "Stripe webhook not implemented yet."}
