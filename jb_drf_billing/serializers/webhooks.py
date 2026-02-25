from rest_framework import serializers


class WebhookPayloadSerializer(serializers.Serializer):
    payload = serializers.JSONField(required=False)
