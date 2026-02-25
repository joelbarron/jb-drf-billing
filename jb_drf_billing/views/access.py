from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.serializers.access import AccessCheckRequestSerializer
from jb_drf_billing.services.access import check_access_batch


class BillingAccessCheckView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        serializer = AccessCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            result = check_access_batch(
                user=request.user,
                features=serializer.validated_data["features"],
                scope_type=serializer.validated_data.get("scopeType", "USER"),
                profile_id=serializer.validated_data.get("profileId"),
                app_slug=serializer.validated_data.get("appSlug") or None,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
