"""Reusable admin classes for jb-drf-billing.

Integrators register their concrete models against these admin classes:

    from django.contrib import admin
    from jb_drf_billing import admin as billing_admin
    from .models import (
        BillingApp, BillingCustomer, Plan, PlanPrice, Subscription,
        Entitlement, PlanEntitlement, EntitlementGrant, BillingEvent,
        CheckoutIntent,
    )

    admin.site.register(BillingApp, billing_admin.BillingAppAdmin)
    admin.site.register(BillingCustomer, billing_admin.BillingCustomerAdmin)
    admin.site.register(Plan, billing_admin.PlanAdmin)
    # ...

Custom columns can be added per-project by subclassing:

    class FinzenioPlanAdmin(billing_admin.PlanAdmin):
        list_display = billing_admin.PlanAdmin.list_display + ("my_custom_field",)
"""

from django.contrib import admin


class BillingAppAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "name", "is_active", "created")
    list_filter = ("is_active",)
    search_fields = ("slug", "name")
    ordering = ("slug",)


class BillingCustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "country_code", "currency_preference", "created")
    search_fields = ("user__email", "user__username")
    list_filter = ("country_code", "currency_preference")
    ordering = ("-id",)
    raw_id_fields = ("user",)


class PlanAdmin(admin.ModelAdmin):
    list_display = ("id", "app", "slug", "name", "tier", "is_active", "created")
    list_filter = ("is_active", "tier", "app")
    search_fields = ("slug", "name")
    ordering = ("app_id", "slug")


class PlanPriceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "plan",
        "slug",
        "interval",
        "currency",
        "amount",
        "country_code",
        "is_active",
        "stripe_price_id",
        "revenuecat_product_id",
    )
    list_filter = ("is_active", "interval", "currency", "country_code")
    search_fields = ("slug", "plan__slug", "stripe_price_id", "revenuecat_product_id")
    ordering = ("plan_id", "slug")


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "billing_customer",
        "plan",
        "provider",
        "status",
        "environment",
        "current_period_end",
        "cancel_at_period_end",
        "modified",
    )
    list_filter = ("provider", "status", "environment", "cancel_at_period_end")
    search_fields = (
        "provider_subscription_id",
        "provider_customer_id",
        "billing_customer__user__email",
        "plan__slug",
    )
    ordering = ("-modified",)
    raw_id_fields = ("billing_customer", "plan", "plan_price")


class EntitlementAdmin(admin.ModelAdmin):
    list_display = ("id", "app", "key", "name", "is_active", "created")
    list_filter = ("is_active", "app")
    search_fields = ("key", "name")
    ordering = ("key",)


class PlanEntitlementAdmin(admin.ModelAdmin):
    list_display = ("id", "plan", "entitlement", "quota")
    search_fields = ("plan__slug", "entitlement__key")
    list_filter = ("plan", "entitlement")
    raw_id_fields = ("plan", "entitlement")


class EntitlementGrantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "app_slug",
        "scope_type",
        "user",
        "profile",
        "entitlement",
        "source_type",
        "is_active",
        "starts_at",
        "ends_at",
        "priority",
    )
    list_filter = ("app_slug", "scope_type", "source_type", "is_active")
    search_fields = ("user__email", "entitlement__key")
    raw_id_fields = ("user", "profile", "entitlement", "subscription")
    ordering = ("-id",)


class BillingEventAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "event_type", "status", "external_event_id", "processed_at", "created")
    list_filter = ("provider", "status", "event_type")
    search_fields = ("external_event_id", "event_type", "payload_hash")
    readonly_fields = ("payload_hash", "payload", "processed_at", "created", "modified")
    ordering = ("-id",)


class CheckoutIntentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "billing_customer",
        "app_slug",
        "plan_price",
        "scope_type",
        "provider",
        "status",
        "provider_session_id",
        "created",
    )
    list_filter = ("app_slug", "provider", "status", "scope_type")
    search_fields = ("provider_session_id", "billing_customer__user__email")
    raw_id_fields = ("billing_customer", "plan_price", "user", "profile")
    ordering = ("-id",)


__all__ = [
    "BillingAppAdmin",
    "BillingCustomerAdmin",
    "PlanAdmin",
    "PlanPriceAdmin",
    "SubscriptionAdmin",
    "EntitlementAdmin",
    "PlanEntitlementAdmin",
    "EntitlementGrantAdmin",
    "BillingEventAdmin",
    "CheckoutIntentAdmin",
]
