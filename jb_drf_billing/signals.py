from django.dispatch import Signal

billing_subscription_activated = Signal()
billing_subscription_changed = Signal()
billing_subscription_canceled = Signal()
billing_entitlements_updated = Signal()
billing_checkout_created = Signal()
billing_webhook_processed = Signal()
