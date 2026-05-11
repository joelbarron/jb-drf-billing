from jb_drf_billing.adapters.revenuecat import RevenueCatAdapter
from jb_drf_billing.adapters.stripe import StripeBillingAdapter
from jb_drf_billing.signals import billing_webhook_processed


def process_revenuecat_webhook(payload, headers=None):
    adapter = RevenueCatAdapter()
    result = adapter.process_webhook(payload or {}, headers=headers)
    billing_webhook_processed.send(sender=process_revenuecat_webhook, provider="revenuecat", result=result)
    return result


def process_stripe_webhook(payload, headers=None):
    adapter = StripeBillingAdapter()
    result = adapter.process_webhook(payload or {}, headers=headers)
    billing_webhook_processed.send(sender=process_stripe_webhook, provider="stripe", result=result)
    return result
