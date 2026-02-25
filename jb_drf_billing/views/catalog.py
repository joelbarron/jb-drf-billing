from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.serializers.catalog import BillingCatalogResponseSerializer
from jb_drf_billing.services.catalog import get_catalog_payload


class BillingCatalogView(APIView):
    permission_classes = [BillingAuthenticated]

    def get(self, request):
        payload = get_catalog_payload(
            user=request.user,
            app_slug=request.query_params.get("app_slug"),
            platform=request.query_params.get("platform"),
            country_code=request.query_params.get("country_code"),
            currency=request.query_params.get("currency"),
        )
        serializer = BillingCatalogResponseSerializer(payload)
        return Response(serializer.data)
