# Phase 4 — Stripe adapter checklist

Phase 4 brings real Stripe support to `jb-drf-billing` (web + Android checkout). All work below is gated by `JB_DRF_BILLING["ENABLE_STRIPE"]=True`. iOS continues to be RevenueCat/IAP only (App Store policy).

Grep entrypoint: `grep -r "TODO\[phase-4-stripe\]" .`

## 1. Stripe products + price mapping
- [ ] Create monthly + yearly products in Stripe Dashboard.
- [ ] Capture each `price_id` (`price_xxx`).
- [ ] Populate `PlanPrice.stripe_price_id` for each integrator. For finzenio, update `api/billing/seeds/billing_catalog.py` `PLANS[1].prices[*].stripe_price_id`.

## 2. `StripeBillingAdapter` (espejo del `RevenueCatAdapter`)

File: `jb_drf_billing/adapters/stripe.py`. Replace stubs with:

- [ ] `__init__`: read `JB_DRF_BILLING["PROVIDERS"]["stripe"]["API_KEY"]` and configure `stripe.api_key`.
- [ ] `_get_or_create_customer(user)`: look up `BillingCustomer.provider_customer_ids["stripe"]["customer_id"]`; if missing, call `stripe.Customer.create(email=user.email, metadata={"userId": user.id})` and persist.
- [ ] `create_checkout_session({user, plan_price, scope_type, profile, success_url, cancel_url, metadata})`:
  ```python
  stripe.checkout.Session.create(
      mode="subscription",
      customer=customer.id,
      line_items=[{"price": plan_price.stripe_price_id, "quantity": 1}],
      success_url=success_url,
      cancel_url=cancel_url,
      metadata={
          "userId": user.id,
          "profileId": profile.id if profile else None,
          "scopeType": scope_type,
          "planPriceId": plan_price.id,
          "appSlug": plan_price.plan.app.slug,
      },
      subscription_data={"trial_period_days": get_setting("TRIAL_DAYS")} if eligible else {},
  )
  ```
  Return `{ok, configured, checkoutUrl: session.url, sessionId: session.id, ...}`.
- [ ] `create_portal_session({user, return_url})`: `stripe.billing_portal.Session.create(customer=..., return_url=...)`.
- [ ] `change_plan(...)`: use Stripe `Subscription.modify` with `proration_behavior="create_prorations"`.
- [ ] `process_webhook(payload, headers)`:
  - Verify signature: `stripe.Webhook.construct_event(payload, headers["Stripe-Signature"], webhook_secret)`.
  - Idempotency: dedupe by `event.id` via `BillingEvent`.
  - Dispatch events:
    - `checkout.session.completed` → look up `CheckoutIntent` by `session.id`, mark `completed`.
    - `customer.subscription.created|updated` → upsert `Subscription` (provider="STRIPE"), then `replace_subscription_grants(subscription=..., user=..., scope_type=...)`.
    - `customer.subscription.deleted` → mark `Subscription.status="canceled"` and let grants expire naturally.
    - `invoice.paid` → bump `current_period_end`.
    - `invoice.payment_failed` → mark `Subscription.status="past_due"`.

## 3. Webhook URL & secret
- [ ] Register `https://<api>/v1/billing/webhooks/stripe` in Stripe Dashboard.
- [ ] Save `whsec_...` in `JB_DRF_BILLING_STRIPE_WEBHOOK_SECRET` env var of QA, then prod.
- [ ] Flip `JB_DRF_BILLING_ENABLE_STRIPE=True` in QA first; smoke test before prod.

## 4. Frontend (`jb-expo-dev-kit` + `jb-react-web-dev-kit`)
- [ ] Implement `BillingClient.createCheckoutSession({planPriceId, scopeType, profileId?, successUrl, cancelUrl})` calling `POST /v1/billing/web/checkout-session`.
- [ ] Implement `useWebCheckoutMutation()` that opens the returned URL in `expo-web-browser` (mobile) or `window.location` (web). Expose only when `Platform.OS in ['android','web']`.
- [ ] Paywall screen branches: iOS → IAP only; Android → IAP + "Pagar con tarjeta" (Stripe); web → Stripe only.

## 5. Tests
- [ ] Webhook idempotency: same `event.id` dispatched twice → second is `BillingEvent.duplicate=True`.
- [ ] Signature failure returns 400 without creating `BillingEvent`.
- [ ] Checkout completed → `Subscription` row exists with provider=STRIPE.

## 6. Migration of legacy `stripe_customer_id`
- [ ] In `finzenio-api`, write a one-shot data migration that copies `User.stripe_customer_id` → `BillingCustomer.provider_customer_ids["stripe"]["customer_id"]` for users where the field is non-null.
- [ ] After verifying, deprecate `User.stripe_customer_id` (keep column for one release with a `DeprecationWarning` in admin).

## 7. Documentation
- [ ] Update `README.md` → mark Stripe section as Production-ready.
- [ ] Add a "Stripe configuration" section to integrator docs covering required env vars, webhook setup, and the `ENABLE_STRIPE` flag.
