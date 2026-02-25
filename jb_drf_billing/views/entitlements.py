from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.services.entitlements import list_effective_entitlements


class BillingEntitlementsView(APIView):
    permission_classes = [BillingAuthenticated]

    def get(self, request):
        app_slug = request.query_params.get("app_slug")
        grants = list_effective_entitlements(request.user, app_slug=app_slug)
        payload = [
            {
                "id": g.id,
                "appSlug": g.app_slug,
                "scopeType": g.scope_type,
                "entitlement": {"id": g.entitlement_id, "key": g.entitlement.key, "name": g.entitlement.name},
                "sourceType": g.source_type,
                "startsAt": g.starts_at,
                "endsAt": g.ends_at,
                "isActive": g.is_active,
                "priority": g.priority,
            }
            for g in grants
        ]
        return Response(payload)
