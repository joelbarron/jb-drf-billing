from rest_framework import serializers


class BillingStatusResponseSerializer(serializers.Serializer):
    appSlug = serializers.CharField(allow_null=True, required=False)
    subscription = serializers.DictField(allow_null=True, required=False)
    entitlements = serializers.DictField(required=False)
    purchaseChannels = serializers.DictField(required=False)
