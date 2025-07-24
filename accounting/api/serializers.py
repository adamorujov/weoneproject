from rest_framework import serializers
from accounting.models import Purchase, Stock, SaleList, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense
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

class StockUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__" 

class SaleListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    sale_datetime = serializers.SerializerMethodField()
    sale_status = serializers.SerializerMethodField()
    class Meta:
        model = SaleList
        fields = "__all__"

    def get_customer(self, obj):
        return obj.salelist_sales.first().customer.username if obj.salelist_sales.exists() else None
    
    def get_seller(self, obj):
        return obj.salelist_sales.first().seller.username if obj.salelist_sales.exists() else None
    
    def get_total_amount(self, obj):
        return sum([sale.price * sale.amount for sale in obj.salelist_sales.all()])
    
    def get_sale_datetime(self, obj):
        return obj.salelist_sales.first().datetime if obj.salelist_sales.exists() else None
    
    def get_sale_status(self, obj):
        return obj.salelist_sales.first().status if obj.salelist_sales.exists() else None

class SaleSerializer(serializers.ModelSerializer):
    seller = CustomUserSerializer()
    customer = CustomUserSerializer()
    product = ProductSerializer()
    class Meta:
        model = Sale
        fields = "__all__"

class SaleListRetrieveSerializer(serializers.ModelSerializer):
    old_debt = serializers.SerializerMethodField()
    new_debt = serializers.SerializerMethodField()
    total_paid_amount = serializers.SerializerMethodField()
    total_debt = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    salelist_sales = SaleSerializer(many=True)
    class Meta:
        model = SaleList
        fields = "__all__"

    def get_old_debt(self, obj):
        old_sales = Sale.objects.exclude(salelist = obj)
        return sum([sale.price * sale.amount for sale in old_sales])

    def get_new_debt(self, obj):
        new_sales = Sale.objects.filter(salelist = obj)
        return sum([sale.price * sale.amount for sale in new_sales])

    def get_total_paid_amount(self, obj):
        customer = obj.salelist_sales.first().customer
        payments = Payment.objects.filter(customer = customer)
        return sum([payment.amount for payment in payments])

    def get_total_debt(self, obj):
        return self.get_old_debt(obj) + self.get_new_debt(obj) - self.get_total_paid_amount(obj)
    
    def get_total_profit(self, obj):
        cost_price = sum([sale.product.cost_price * sale.amount for sale in obj.salelist_sales.all()])
        return self.get_new_debt(obj) - cost_price

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
    statuses = serializers.ListField(child=serializers.CharField(), allow_empty=False)

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
