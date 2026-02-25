from jb_drf_billing.catalog.base import BaseCatalogProvider
from jb_drf_billing.conf import get_app_slug, resolve_model


class DBCatalogProvider(BaseCatalogProvider):
    def get_catalog(self, *, user=None, app_slug=None, platform=None, country_code=None, currency=None):
        BillingApp = resolve_model("PLAN_MODEL")._meta.get_field("app").remote_field.model
        Plan = resolve_model("PLAN_MODEL")
        PlanPrice = resolve_model("PLAN_PRICE_MODEL")
        PlanEntitlement = resolve_model("PLAN_ENTITLEMENT_MODEL")

        slug = app_slug or get_app_slug()
        apps_qs = BillingApp.objects.filter(is_active=True)
        if slug:
            apps_qs = apps_qs.filter(slug=slug)
        app_map = {a.id: a for a in apps_qs}
        plans = Plan.objects.filter(app_id__in=app_map.keys(), is_active=True).order_by("id")
        plan_ids = [p.id for p in plans]
        prices_qs = PlanPrice.objects.filter(plan_id__in=plan_ids, is_active=True).order_by("id")
        if country_code:
            prices_qs = prices_qs.filter(country_code__in=[country_code.upper(), None])
        if currency:
            prices_qs = prices_qs.filter(currency__iexact=currency)
        plan_entitlements = PlanEntitlement.objects.filter(plan_id__in=plan_ids).select_related("entitlement")

        prices_by_plan = {}
        for price in prices_qs:
            prices_by_plan.setdefault(price.plan_id, []).append(price)
        ents_by_plan = {}
        for pe in plan_entitlements:
            ents_by_plan.setdefault(pe.plan_id, []).append(pe)

        return {
            "appSlug": slug,
            "purchaseChannels": {
                "ios": ["iap"],
                "android": ["iap", "web"],
                "web": ["web"],
            },
            "plans": [
                {
                    "id": p.id,
                    "slug": p.slug,
                    "name": p.name,
                    "description": p.description,
                    "tier": p.tier,
                    "prices": [
                        {
                            "id": pr.id,
                            "slug": pr.slug,
                            "interval": pr.interval,
                            "currency": pr.currency,
                            "countryCode": pr.country_code,
                            "amount": str(pr.amount),
                        }
                        for pr in prices_by_plan.get(p.id, [])
                    ],
                    "entitlements": [
                        {
                            "id": pe.entitlement_id,
                            "key": pe.entitlement.key,
                            "name": pe.entitlement.name,
                            "quota": pe.quota,
                            "flags": pe.flags,
                        }
                        for pe in ents_by_plan.get(p.id, [])
                    ],
                }
                for p in plans
            ],
        }
