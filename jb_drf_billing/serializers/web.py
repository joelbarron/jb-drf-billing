from rest_framework import serializers


class CheckoutSessionRequestSerializer(serializers.Serializer):
    appSlug = serializers.CharField(required=False)
    planPriceId = serializers.IntegerField()
    scopeType = serializers.ChoiceField(choices=["USER", "PROFILE"])
    profileId = serializers.IntegerField(required=False, allow_null=True)
    successUrl = serializers.URLField()
    cancelUrl = serializers.URLField()


class ChangePlanRequestSerializer(serializers.Serializer):
    planPriceId = serializers.IntegerField()
    scopeType = serializers.ChoiceField(choices=["USER", "PROFILE"], required=False, default="USER")
    profileId = serializers.IntegerField(required=False, allow_null=True)
