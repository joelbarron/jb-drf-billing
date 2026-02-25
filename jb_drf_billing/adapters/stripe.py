from .base import BillingProviderAdapter


class StripeBillingAdapter(BillingProviderAdapter):
    provider_name = "stripe"

    def sync_customer(self, *args, **kwargs):
        return {"synced": False}

    def process_webhook(self, *args, **kwargs):
        return {"processed": False}
