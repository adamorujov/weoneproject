from rest_framework import serializers
from accounting.models import Purchase, Sale, Payment, ProductAction, CustomerAction
from core.api.serializers import ProductSerializer, CustomUserRetrieveSerializer

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

class SaleSerializer(serializers.ModelSerializer):
    customer = CustomUserRetrieveSerializer()
    product = ProductSerializer()
    class Meta:
        model = Sale
        fields = "__all__"

class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"
    
class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomUserRetrieveSerializer()
    class Meta:
        model = Payment
        fields = "__all__"

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class ProductActionSerializer(serializers.ModelSerializer):
    customer = CustomUserRetrieveSerializer()
    product = ProductSerializer()
    class Meta:
        model = ProductAction
        fields = "__all__"

class CustomerActionSerializer(serializers.ModelSerializer):
    customer = CustomUserRetrieveSerializer()
    product = ProductSerializer()
    class Meta:
        model = CustomerAction
        fields = "__all__"
