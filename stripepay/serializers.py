from rest_framework import serializers

class PaymentIntentRequestSerializer(serializers.Serializer):
    product_name = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(default=1)
