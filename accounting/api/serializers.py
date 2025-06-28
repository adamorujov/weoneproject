from rest_framework import serializers
from accounting.models import Purchase
from core.api.serializers import ProductSerializer

class PurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ("product", "amount", "status", "date")

class PurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = "__all__"

class AddToStockSerializer(serializers.ModelSerializer):
    item_ids = serializers.ListField(
        child = serializers.IntegerField(), allow_empty=False
    )