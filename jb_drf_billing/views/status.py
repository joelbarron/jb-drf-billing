from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.serializers.status import BillingStatusResponseSerializer
from jb_drf_billing.services.status import get_billing_status


class BillingStatusView(APIView):
    permission_classes = [BillingAuthenticated]

    def get(self, request):
        payload = get_billing_status(user=request.user, app_slug=request.query_params.get("app_slug"))
        return Response(BillingStatusResponseSerializer(payload).data)
