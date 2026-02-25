from rest_framework.response import Response
from rest_framework.views import APIView

from jb_drf_billing.permissions import BillingAuthenticated
from jb_drf_billing.serializers.web import CheckoutSessionRequestSerializer, ChangePlanRequestSerializer
from jb_drf_billing.services.web_checkout import create_checkout_session, create_portal_session


class BillingWebCheckoutSessionView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(create_checkout_session(user=request.user, payload=serializer.validated_data))


class BillingWebPortalSessionView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        return Response(create_portal_session(user=request.user))


class BillingWebChangePlanView(APIView):
    permission_classes = [BillingAuthenticated]

    def post(self, request):
        serializer = ChangePlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"ok": False, "message": "Change plan not implemented yet.", "payload": serializer.validated_data})
