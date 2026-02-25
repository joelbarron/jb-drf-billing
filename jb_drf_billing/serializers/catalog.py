from rest_framework import serializers


class BillingCatalogResponseSerializer(serializers.Serializer):
    appSlug = serializers.CharField(allow_null=True, required=False)
    purchaseChannels = serializers.DictField(required=False)
    plans = serializers.ListField(child=serializers.DictField(), required=False)
