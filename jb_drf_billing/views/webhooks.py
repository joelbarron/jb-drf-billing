from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from jb_drf_billing.services.webhooks import process_revenuecat_webhook, process_stripe_webhook


class RevenueCatWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = process_revenuecat_webhook(request.data, headers=request.headers)
        code = status.HTTP_200_OK if payload.get("ok", False) else status.HTTP_401_UNAUTHORIZED
        return Response(payload, status=code)


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = process_stripe_webhook(request.data, headers=request.headers)
        code = status.HTTP_200_OK if payload.get("ok", False) else status.HTTP_400_BAD_REQUEST
        return Response(payload, status=code)
