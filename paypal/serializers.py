from rest_framework import serializers
from .models import Order


class PayPalOrderRequestSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=255)
    amount = serializers.IntegerField(min_value=1, help_text="Montant unitaire en cents")
    quantity = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(max_length=3, default='USD')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'