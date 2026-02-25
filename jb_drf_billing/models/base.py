from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from jb_drf_auth.conf import get_setting as get_auth_setting


class AbstractTimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractBillingApp(AbstractTimeStampedModel):
    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        ordering = ["slug"]

    def __str__(self):
        return self.slug


class AbstractBillingCustomer(AbstractTimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    provider_customer_ids = models.JSONField(default=dict, blank=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    currency_preference = models.CharField(max_length=3, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["user"])]


class AbstractPlan(AbstractTimeStampedModel):
    app = models.ForeignKey("billing.BillingApp", on_delete=models.CASCADE, related_name="plans")
    slug = models.SlugField(max_length=120)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    tier = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        unique_together = (("app", "slug"),)
        ordering = ["app_id", "slug"]

    def __str__(self):
        return self.slug


class AbstractPlanPrice(AbstractTimeStampedModel):
    INTERVAL_CHOICES = (("monthly", "Monthly"), ("yearly", "Yearly"), ("one_time", "One Time"))

    plan = models.ForeignKey("billing.Plan", on_delete=models.CASCADE, related_name="prices")
    slug = models.SlugField(max_length=160)
    interval = models.CharField(max_length=20, choices=INTERVAL_CHOICES)
    currency = models.CharField(max_length=3)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    revenuecat_product_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    revenuecat_entitlement_key = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        unique_together = (("plan", "slug"),)
        ordering = ["plan_id", "slug"]


class AbstractSubscription(AbstractTimeStampedModel):
    PROVIDER_CHOICES = (("REVENUECAT", "RevenueCat"), ("STRIPE", "Stripe"))
    STATUS_CHOICES = (
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("grace_period", "Grace period"),
        ("past_due", "Past due"),
        ("canceled", "Canceled"),
        ("expired", "Expired"),
        ("paused", "Paused"),
    )
    ENV_CHOICES = (("sandbox", "Sandbox"), ("production", "Production"))

    billing_customer = models.ForeignKey("billing.BillingCustomer", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey("billing.Plan", on_delete=models.CASCADE, related_name="subscriptions")
    plan_price = models.ForeignKey("billing.PlanPrice", on_delete=models.SET_NULL, null=True, blank=True, related_name="subscriptions")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_subscription_id = models.CharField(max_length=255, db_index=True)
    provider_customer_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    environment = models.CharField(max_length=20, choices=ENV_CHOICES, default="production")
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(blank=True, null=True)
    raw_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        unique_together = (("provider", "provider_subscription_id"),)


class AbstractEntitlement(AbstractTimeStampedModel):
    app = models.ForeignKey("billing.BillingApp", on_delete=models.CASCADE, related_name="entitlements")
    key = models.CharField(max_length=160, db_index=True)
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        unique_together = (("app", "key"),)
        ordering = ["key"]


class AbstractPlanEntitlement(AbstractTimeStampedModel):
    plan = models.ForeignKey("billing.Plan", on_delete=models.CASCADE, related_name="plan_entitlements")
    entitlement = models.ForeignKey("billing.Entitlement", on_delete=models.CASCADE, related_name="plan_entitlements")
    quota = models.IntegerField(blank=True, null=True)
    flags = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        unique_together = (("plan", "entitlement"),)


class AbstractEntitlementGrant(AbstractTimeStampedModel):
    SCOPE_CHOICES = (("USER", "User"), ("PROFILE", "Profile"))
    SOURCE_CHOICES = (
        ("SUBSCRIPTION", "Subscription"),
        ("PROMOTION", "Promotion"),
        ("MANUAL", "Manual"),
        ("TRIAL", "Trial"),
        ("COMP", "Comp"),
    )

    _profile_model = get_auth_setting("PROFILE_MODEL") or "authentication.Profile"

    app_slug = models.SlugField(max_length=80, db_index=True)
    scope_type = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="billing_entitlement_grants")
    profile = models.ForeignKey(_profile_model, on_delete=models.CASCADE, null=True, blank=True, related_name="billing_entitlement_grants")
    entitlement = models.ForeignKey("billing.Entitlement", on_delete=models.CASCADE, related_name="grants")
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="SUBSCRIPTION")
    subscription = models.ForeignKey("billing.Subscription", on_delete=models.SET_NULL, null=True, blank=True, related_name="grants")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=100)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["app_slug", "scope_type", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def clean(self):
        if self.scope_type == "USER":
            if not self.user_id:
                raise ValidationError({"user": "user is required when scope_type=USER"})
            if self.profile_id:
                raise ValidationError({"profile": "profile must be null when scope_type=USER"})
        if self.scope_type == "PROFILE" and not self.profile_id:
            raise ValidationError({"profile": "profile is required when scope_type=PROFILE"})


class AbstractBillingEvent(AbstractTimeStampedModel):
    STATUS_CHOICES = (("received", "Received"), ("processed", "Processed"), ("ignored", "Ignored"), ("failed", "Failed"))

    provider = models.CharField(max_length=40, db_index=True)
    event_type = models.CharField(max_length=120)
    external_event_id = models.CharField(max_length=255)
    payload_hash = models.CharField(max_length=64, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    error_message = models.TextField(blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = (("provider", "external_event_id"),)


class AbstractCheckoutIntent(AbstractTimeStampedModel):
    STATUS_CHOICES = (("created", "Created"), ("submitted", "Submitted"), ("completed", "Completed"), ("expired", "Expired"), ("canceled", "Canceled"))
    PROVIDER_CHOICES = (("STRIPE", "Stripe"),)

    billing_customer = models.ForeignKey("billing.BillingCustomer", on_delete=models.CASCADE, related_name="checkout_intents")
    app_slug = models.SlugField(max_length=80, db_index=True)
    plan_price = models.ForeignKey("billing.PlanPrice", on_delete=models.CASCADE, related_name="checkout_intents")
    scope_type = models.CharField(max_length=20, choices=AbstractEntitlementGrant.SCOPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="billing_checkout_intents")
    profile = models.ForeignKey(AbstractEntitlementGrant._profile_model, on_delete=models.CASCADE, null=True, blank=True, related_name="billing_checkout_intents")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default="STRIPE")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    success_url = models.URLField(max_length=1000)
    cancel_url = models.URLField(max_length=1000)
    provider_session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True
