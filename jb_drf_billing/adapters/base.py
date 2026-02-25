class BillingProviderAdapter:
    provider_name = None

    def sync_customer(self, *args, **kwargs):
        raise NotImplementedError

    def process_webhook(self, *args, **kwargs):
        raise NotImplementedError
