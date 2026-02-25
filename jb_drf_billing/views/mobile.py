from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.serializers.mobile import MobileSyncRequestSerializer
from jb_drf_billing.services.mobile_sync import sync_mobile_billing


class BillingMobileSyncView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        serializer = MobileSyncRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        return Response(
            sync_mobile_billing(
                user=request.user,
                platform=payload.get("platform"),
                app_user_id=payload.get("appUserId"),
            )
        )


class BillingMobileRestoreAckView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        return Response({"ok": True, "acknowledged": True})
