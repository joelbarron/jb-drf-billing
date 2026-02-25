from rest_framework import serializers


class MobileSyncRequestSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=["ios", "android"], required=False)
    appUserId = serializers.CharField(required=False, allow_blank=True)
