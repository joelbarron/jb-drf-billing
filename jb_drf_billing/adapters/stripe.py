"""Stripe billing adapter.

Stable stub: signatures are stable and the module imports without Stripe
credentials so the lib can be installed and tested in projects that have
not enabled Stripe yet. Methods that perform real I/O raise a clear
NotImplementedError pointing to the next implementation phase.

# TODO[phase-4-stripe]: replace stubs with real Stripe SDK calls.
# Required:
#   - Checkout Session create (stripe.checkout.Session.create) with
#     metadata {userId, profileId, scopeType, planPriceId}.
#   - Customer Portal Session create.
#   - Webhook signature verify (stripe.Webhook.construct_event) +
#     event dispatch: checkout.session.completed, customer.subscription.
#     {updated,deleted}, invoice.{paid,payment_failed}.
#   - Customer get-or-create via BillingCustomer.provider_customer_ids['stripe'].
#   - Update upon webhook → call replace_subscription_grants() like RevenueCat.
# See PHASE_4_TODO.md at the repo root for the full checklist.
"""

from typing import Any

from jb_drf_billing.adapters.base import BillingProviderAdapter
from jb_drf_billing.conf import get_providers_settings


PENDING_MESSAGE = "Stripe adapter pending — Phase 4 of jb-drf-billing roadmap."


class StripeBillingAdapter(BillingProviderAdapter):
    provider_name = "stripe"

    def __init__(self):
        self.provider_cfg = (get_providers_settings() or {}).get("stripe", {}) or {}

    # ----- Catalog / config -------------------------------------------------

    def is_configured(self) -> bool:
        return bool(self.provider_cfg.get("API_KEY"))

    # ----- Checkout / portal ------------------------------------------------

    def create_checkout_session(
        self,
        *,
        user: Any,
        plan_price: Any,
        scope_type: str,
        profile: Any = None,
        success_url: str,
        cancel_url: str,
        metadata: dict | None = None,
    ) -> dict:
        """Stub: returns a sentinel URL so callers can integrate end-to-end
        without real Stripe credentials. Will be replaced in Phase 4.
        """
        return {
            "ok": False,
            "provider": "stripe",
            "configured": self.is_configured(),
            "checkoutUrl": "stub://stripe-not-configured",
            "sessionId": None,
            "message": PENDING_MESSAGE,
            "metadata": metadata or {},
        }

    def create_portal_session(self, *, user: Any, return_url: str | None = None) -> dict:
        return {
            "ok": False,
            "provider": "stripe",
            "configured": self.is_configured(),
            "portalUrl": "stub://stripe-not-configured",
            "message": PENDING_MESSAGE,
        }

    def change_plan(self, *, user: Any, plan_price: Any, scope_type: str, profile: Any = None) -> dict:
        return {
            "ok": False,
            "provider": "stripe",
            "configured": self.is_configured(),
            "message": PENDING_MESSAGE,
        }

    # ----- Provider parity --------------------------------------------------

    def sync_customer(self, *args, **kwargs):
        raise NotImplementedError(PENDING_MESSAGE)

    def process_webhook(self, payload, headers=None):
        return {
            "ok": True,
            "processed": False,
            "provider": "stripe",
            "configured": self.is_configured(),
            "message": PENDING_MESSAGE,
        }
