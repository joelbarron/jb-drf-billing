import hashlib
import json
from datetime import datetime, timezone as dt_timezone
from typing import Any
from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from jb_drf_billing.adapters.base import BillingProviderAdapter
from jb_drf_billing.conf import get_app_slug, get_providers_settings, resolve_model
from jb_drf_billing.services.entitlements import replace_subscription_grants


class RevenueCatAdapter(BillingProviderAdapter):
    provider_name = "revenuecat"

    def __init__(self):
        self.provider_cfg = (get_providers_settings() or {}).get("revenuecat", {}) or {}

    def build_app_user_id(self, user, *, app_slug: str | None = None) -> str:
        return f"{app_slug or get_app_slug()}:user:{user.id}"

    def parse_app_user_id(self, app_user_id: str | None):
        if not app_user_id or not isinstance(app_user_id, str):
            return None, None
        parts = app_user_id.split(":")
        if len(parts) >= 3 and parts[-2] == "user":
            try:
                return ":".join(parts[:-2]), int(parts[-1])
            except ValueError:
                return None, None
        return None, None

    def _parse_dt(self, value: Any):
        if value in (None, "", 0):
            return None
        if isinstance(value, (int, float)):
            # RevenueCat often sends *_ms fields
            if value > 10_000_000_000:
                return datetime.fromtimestamp(value / 1000, tz=dt_timezone.utc)
            return datetime.fromtimestamp(value, tz=dt_timezone.utc)
        if isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                return None
            if candidate.endswith("Z"):
                candidate = candidate.replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(candidate)
                return dt if dt.tzinfo else dt.replace(tzinfo=dt_timezone.utc)
            except ValueError:
                return None
        return None

    def _infer_env(self, data: dict[str, Any]):
        env = (data.get("environment") or "").lower()
        if env in {"sandbox", "production"}:
            return env
        if data.get("is_sandbox") is True:
            return "sandbox"
        return "production"

    def _infer_status(self, *, expires_at, unsubscribed_at=None, event_type: str | None = None):
        now = timezone.now()
        event_type_norm = (event_type or "").upper()
        if event_type_norm in {"CANCELLATION", "EXPIRATION", "SUBSCRIPTION_EXPIRED"}:
            if expires_at and expires_at > now:
                return "canceled"
            return "expired"
        if unsubscribed_at and expires_at and expires_at > now:
            return "canceled"
        if expires_at and expires_at <= now:
            return "expired"
        return "active"

    def _payload_hash(self, payload: dict[str, Any]) -> str:
        try:
            serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        except TypeError:
            serialized = json.dumps(str(payload))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def _event_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = payload.get("event") if isinstance(payload, dict) else None
        return event if isinstance(event, dict) else (payload if isinstance(payload, dict) else {})

    def _validate_webhook_secret(self, headers):
        expected = self.provider_cfg.get("WEBHOOK_SECRET")
        if not expected:
            return True
        header_name = str(self.provider_cfg.get("WEBHOOK_AUTH_HEADER") or "authorization").lower()
        got = None
        for key, value in (headers or {}).items():
            if str(key).lower() == header_name:
                got = value
                break
        if got is None:
            return False
        got_str = str(got).strip()
        if got_str.lower().startswith("bearer "):
            got_str = got_str[7:].strip()
        return got_str == str(expected).strip()

    def _resolve_user_from_app_user_id(self, app_user_id: str | None):
        _, user_id = self.parse_app_user_id(app_user_id)
        if not user_id:
            return None
        User = get_user_model()
        return User.objects.filter(id=user_id).first()

    def _get_or_create_billing_customer(self, *, user, app_user_id=None, aliases=None):
        BillingCustomer = resolve_model("BILLING_CUSTOMER_MODEL")
        customer, _ = BillingCustomer.objects.get_or_create(user=user, defaults={"provider_customer_ids": {}})
        provider_ids = dict(customer.provider_customer_ids or {})
        rc_meta = dict(provider_ids.get("revenuecat") or {})
        if app_user_id:
            rc_meta["app_user_id"] = app_user_id
        if aliases:
            rc_meta["aliases"] = sorted({str(a) for a in aliases if a})
        if rc_meta:
            provider_ids["revenuecat"] = rc_meta
            customer.provider_customer_ids = provider_ids
            customer.save(update_fields=["provider_customer_ids", "modified"])
        return customer

    def _resolve_plan_price_by_product_id(self, product_id: str | None):
        if not product_id:
            return None
        PlanPrice = resolve_model("PLAN_PRICE_MODEL")
        return PlanPrice.objects.select_related("plan", "plan__app").filter(revenuecat_product_id=product_id).first()

    def _upsert_subscription_from_data(
        self,
        *,
        billing_customer,
        plan_price,
        app_user_id,
        product_id,
        event_type=None,
        source_data: dict[str, Any],
    ):
        Subscription = resolve_model("SUBSCRIPTION_MODEL")
        provider_subscription_id = (
            source_data.get("original_transaction_id")
            or source_data.get("transaction_id")
            or source_data.get("id")
            or f"{app_user_id}:{product_id}"
        )
        expires_at = self._parse_dt(
            source_data.get("expires_at_ms")
            or source_data.get("expiration_at_ms")
            or source_data.get("expires_date")
            or source_data.get("expires_date_ms")
        )
        purchased_at = self._parse_dt(
            source_data.get("purchased_at_ms")
            or source_data.get("purchase_date_ms")
            or source_data.get("purchased_at")
            or source_data.get("purchase_date")
        )
        unsubscribed_at = self._parse_dt(source_data.get("unsubscribe_detected_at") or source_data.get("canceled_at_ms"))
        status = self._infer_status(expires_at=expires_at, unsubscribed_at=unsubscribed_at, event_type=event_type)
        environment = self._infer_env(source_data)
        defaults = {
            "billing_customer": billing_customer,
            "plan": plan_price.plan,
            "plan_price": plan_price,
            "provider_customer_id": app_user_id,
            "status": status,
            "environment": environment,
            "current_period_start": purchased_at,
            "current_period_end": expires_at,
            "cancel_at_period_end": status == "canceled",
            "canceled_at": unsubscribed_at,
            "raw_snapshot": source_data,
        }
        subscription, created = Subscription.objects.update_or_create(
            provider="REVENUECAT",
            provider_subscription_id=str(provider_subscription_id),
            defaults=defaults,
        )
        return subscription, created

    def _apply_grants_for_subscription(self, subscription, *, user, event_data=None):
        scope_type = "USER"
        profile = None
        # Future: parse profile assignment from custom metadata.
        return replace_subscription_grants(
            subscription=subscription,
            scope_type=scope_type,
            user=user,
            profile=profile,
            app_slug=getattr(subscription.plan.app, "slug", None),
        )

    def _process_revenuecat_event(self, *, event_data: dict[str, Any]):
        event_type = event_data.get("type")
        app_user_id = event_data.get("app_user_id") or event_data.get("original_app_user_id")
        aliases = event_data.get("aliases") or []
        user = self._resolve_user_from_app_user_id(app_user_id)
        if not user:
            return {
                "processed": False,
                "reason": "user_not_found",
                "appUserId": app_user_id,
                "eventType": event_type,
            }

        product_id = event_data.get("product_id")
        plan_price = self._resolve_plan_price_by_product_id(product_id)
        if not plan_price:
            return {
                "processed": False,
                "reason": "plan_price_not_mapped",
                "appUserId": app_user_id,
                "productId": product_id,
                "eventType": event_type,
            }

        billing_customer = self._get_or_create_billing_customer(user=user, app_user_id=app_user_id, aliases=aliases)
        subscription, created = self._upsert_subscription_from_data(
            billing_customer=billing_customer,
            plan_price=plan_price,
            app_user_id=app_user_id,
            product_id=product_id,
            event_type=event_type,
            source_data=event_data,
        )
        created_grants = self._apply_grants_for_subscription(subscription, user=user, event_data=event_data)
        return {
            "processed": True,
            "eventType": event_type,
            "appUserId": app_user_id,
            "productId": product_id,
            "subscriptionId": subscription.id,
            "subscriptionStatus": subscription.status,
            "subscriptionCreated": created,
            "grantsCreated": len(created_grants),
        }

    def process_webhook(self, payload: dict[str, Any], headers=None):
        if not self._validate_webhook_secret(headers):
            return {"ok": False, "processed": False, "provider": "revenuecat", "reason": "invalid_webhook_secret"}

        BillingEvent = resolve_model("BILLING_EVENT_MODEL")
        wrapper = payload if isinstance(payload, dict) else {}
        event_data = self._event_payload(wrapper)
        event_id = (
            event_data.get("id")
            or wrapper.get("id")
            or f"{event_data.get('type','UNKNOWN')}:{event_data.get('app_user_id','')}:{event_data.get('event_timestamp_ms') or event_data.get('purchased_at_ms') or timezone.now().timestamp()}"
        )
        payload_hash = self._payload_hash(wrapper)

        with transaction.atomic():
            event, created = BillingEvent.objects.get_or_create(
                provider="revenuecat",
                external_event_id=str(event_id),
                defaults={
                    "event_type": str(event_data.get("type") or wrapper.get("type") or "unknown"),
                    "payload_hash": payload_hash,
                    "payload": wrapper,
                    "status": "received",
                },
            )
            if not created:
                return {
                    "ok": True,
                    "processed": False,
                    "provider": "revenuecat",
                    "duplicate": True,
                    "eventId": str(event_id),
                    "status": event.status,
                }
            try:
                result = self._process_revenuecat_event(event_data=event_data)
                event.status = "processed" if result.get("processed") else "ignored"
                event.processed_at = timezone.now()
                event.payload_hash = payload_hash
                event.payload = wrapper
                event.save(update_fields=["status", "processed_at", "payload_hash", "payload", "modified"])
                return {"ok": True, "provider": "revenuecat", "eventId": str(event_id), **result}
            except Exception as exc:
                event.status = "failed"
                event.error_message = str(exc)
                event.processed_at = timezone.now()
                event.payload_hash = payload_hash
                event.payload = wrapper
                event.save(update_fields=["status", "error_message", "processed_at", "payload_hash", "payload", "modified"])
                raise

    def _fetch_subscriber(self, app_user_id: str):
        import requests

        api_key = self.provider_cfg.get("API_KEY")
        if not api_key:
            raise ValueError("RevenueCat API key is not configured.")
        base_url = str(self.provider_cfg.get("API_BASE_URL") or "https://api.revenuecat.com").rstrip("/")
        timeout = int(self.provider_cfg.get("REQUEST_TIMEOUT_SECONDS") or 15)
        url = f"{base_url}/v1/subscribers/{quote(app_user_id, safe='')}"
        response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("subscriber"), dict):
            raise ValueError("Unexpected RevenueCat subscriber payload.")
        return payload

    def _subscription_records_from_subscriber(self, subscriber_payload: dict[str, Any]):
        subscriber = subscriber_payload.get("subscriber") or {}
        subscriptions = subscriber.get("subscriptions") or {}
        records = []
        for product_id, sub_data in subscriptions.items():
            if not isinstance(sub_data, dict):
                continue
            data = dict(sub_data)
            data.setdefault("product_id", product_id)
            records.append(data)
        # Most recent first if we can infer
        records.sort(
            key=lambda item: (
                self._parse_dt(item.get("purchase_date") or item.get("purchased_at") or item.get("purchase_date_ms"))
                or datetime(1970, 1, 1, tzinfo=dt_timezone.utc)
            ),
            reverse=True,
        )
        return subscriber, records

    @transaction.atomic
    def sync_customer(self, *, user, app_user_id=None, platform=None):
        resolved_app_user_id = app_user_id or self.build_app_user_id(user)
        payload = self._fetch_subscriber(resolved_app_user_id)
        subscriber, records = self._subscription_records_from_subscriber(payload)
        aliases = subscriber.get("aliases") or []
        billing_customer = self._get_or_create_billing_customer(user=user, app_user_id=resolved_app_user_id, aliases=aliases)

        processed = []
        for record in records:
            product_id = record.get("product_id")
            plan_price = self._resolve_plan_price_by_product_id(product_id)
            if not plan_price:
                continue
            subscription, created = self._upsert_subscription_from_data(
                billing_customer=billing_customer,
                plan_price=plan_price,
                app_user_id=resolved_app_user_id,
                product_id=product_id,
                event_type="SYNC",
                source_data=record,
            )
            grants = self._apply_grants_for_subscription(subscription, user=user, event_data=record)
            processed.append(
                {
                    "subscriptionId": subscription.id,
                    "subscriptionCreated": created,
                    "status": subscription.status,
                    "productId": product_id,
                    "planSlug": subscription.plan.slug,
                    "grantsCreated": len(grants),
                }
            )

        return {
            "ok": True,
            "provider": "revenuecat",
            "synced": True,
            "platform": platform,
            "appUserId": resolved_app_user_id,
            "subscriptionsProcessed": processed,
            "subscriberFound": True,
        }
