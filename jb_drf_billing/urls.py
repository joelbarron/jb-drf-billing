from django.urls import path

from jb_drf_billing.views import (
    BillingAccessCheckView,
    BillingCatalogView,
    BillingEntitlementsView,
    BillingMobileRestoreAckView,
    BillingMobileSyncView,
    BillingStatusView,
    BillingWebChangePlanView,
    BillingWebCheckoutSessionView,
    BillingWebPortalSessionView,
    RevenueCatWebhookView,
    StripeWebhookView,
)

urlpatterns = [
    path("catalog", BillingCatalogView.as_view(), name="billing-catalog"),
    path("status", BillingStatusView.as_view(), name="billing-status"),
    path("entitlements", BillingEntitlementsView.as_view(), name="billing-entitlements"),
    path("access/check", BillingAccessCheckView.as_view(), name="billing-access-check"),
    path("mobile/sync", BillingMobileSyncView.as_view(), name="billing-mobile-sync"),
    path("mobile/restore/ack", BillingMobileRestoreAckView.as_view(), name="billing-mobile-restore-ack"),
    path("web/checkout-session", BillingWebCheckoutSessionView.as_view(), name="billing-web-checkout-session"),
    path("web/portal-session", BillingWebPortalSessionView.as_view(), name="billing-web-portal-session"),
    path("web/change-plan", BillingWebChangePlanView.as_view(), name="billing-web-change-plan"),
    path("webhooks/revenuecat", RevenueCatWebhookView.as_view(), name="billing-webhook-revenuecat"),
    path("webhooks/stripe", StripeWebhookView.as_view(), name="billing-webhook-stripe"),
]
