from rest_framework import serializers


class AccessCheckRequestSerializer(serializers.Serializer):
    scopeType = serializers.ChoiceField(choices=["USER", "PROFILE"], default="USER")
    profileId = serializers.IntegerField(required=False, allow_null=True)
    features = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    appSlug = serializers.CharField(required=False, allow_blank=True)


class AccessCheckResponseItemSerializer(serializers.Serializer):
    featureKey = serializers.CharField()
    enabled = serializers.BooleanField()
    reason = serializers.CharField(allow_null=True, required=False)
    source = serializers.CharField(allow_null=True, required=False)
    scopeType = serializers.CharField(required=False)
