from rest_framework import serializers
from accounting.models import Purchase, Stock, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense
from core.api.serializers import ProductSerializer, CustomUserSerializer

class PurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ("supplier", "product", "amount", "status", "date")

class PurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = "__all__"

class AddToStockSerializer(serializers.Serializer):
    item_ids = serializers.ListField(
        child = serializers.IntegerField(), allow_empty=False
    )

class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Stock
        fields = "__all__" 

class SaleSerializer(serializers.ModelSerializer):
    customer = CustomUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = Sale
        fields = "__all__"

class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"
    
class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomUserSerializer()
    class Meta:
        model = Payment
        fields = "__all__"

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class ProductActionSerializer(serializers.ModelSerializer):
    customer = CustomUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = ProductAction
        fields = "__all__"

class CustomerActionSerializer(serializers.ModelSerializer):
    customer = CustomUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = CustomerAction
        fields = "__all__"


class BulkSaleSerializer(serializers.Serializer):
    customer = serializers.IntegerField()
    products = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    prices = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    amounts = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    datetimes = serializers.ListField(child=serializers.DateTimeField(), allow_empty=False)

class ReturnBackSerializer(serializers.ModelSerializer):
    sale = SaleSerializer()
    class Meta:
        model = ReturnBack
        fields = "__all__"

class ReturnBackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnBack
        fields = "__all__"

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = "__all__"
