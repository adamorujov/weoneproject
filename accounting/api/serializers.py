from rest_framework import serializers
from accounting.models import PurchaseList, Purchase, Stock, SaleList, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense, SupplierPayment
from core.api.serializers import ProductSerializer, CustomUserSerializer

class PurchaseListSerializer(serializers.ModelSerializer):
    supplier = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    purchase_price = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseList
        fields = "__all__"

    def _get_total(self, obj, attr_name):
        purchases = obj.purchaselist_purchases.all()
        return sum(getattr(purchase.product, attr_name, 0) * purchase.amount for purchase in purchases if purchase.product)

    def get_supplier(self, obj):
        supplier = obj.purchaselist_purchases.first().supplier
        return CustomUserSerializer(instance=supplier).data
    
    def get_amount(self, obj):
        return sum([purchase.amount for purchase in obj.purchaselist_purchases.all()])
    
    def get_purchase_price(self, obj):
        return self._get_total(obj, "purchase_price")

    def get_cost_price(self, obj):
        return self._get_total(obj, "cost_price")

    def get_price(self, obj):
        return self._get_total(obj, "price")

    def get_discount_price(self, obj):
        return self._get_total(obj, "discount_price")
    
    def get_status(self, obj):
        return obj.purchaselist_purchases.first().status
    
    def get_date(self, obj):
        return obj.purchaselist_purchases.first().date
    
class PurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ("supplier", "product", "amount", "status", "date")

class PurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Purchase
        fields = "__all__"

class PurchaseListRetrieveSerializer(serializers.ModelSerializer):
    purchaselist_purchases = PurchaseSerializer(many=True)
    class Meta:
        model = PurchaseList
        fields = "__all__"

class PurchaseListUpdateSerializer(serializers.Serializer):
    currency = serializers.CharField(allow_blank=True)
    status = serializers.CharField(allow_blank=True)
    date = serializers.DateField(allow_null=True)

class PurchaseListDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseList
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
        return sum([sale.price * sale.amount for sale in obj.salelist_sales.filter(status="S")])
    
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
    paid_amount = serializers.SerializerMethodField()
    total_debt = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    salelist_sales = SaleSerializer(many=True)
    class Meta:
        model = SaleList
        fields = "__all__"

    def get_old_debt(self, obj):
        customer = obj.salelist_sales.first().customer
        dt = obj.salelist_sales.first().datetime
        old_sales = Sale.objects.filter(customer=customer, status="S", datetime__lt=dt)
        total_old_price = sum([sale.price * sale.amount for sale in old_sales])
        total_old_debt = total_old_price - self.get_total_paid_amount(obj)
        return total_old_debt if total_old_debt > 0 else 0

    def get_new_debt(self, obj):
        customer = obj.salelist_sales.first().customer
        dt = obj.salelist_sales.first().datetime
        old_sales = Sale.objects.filter(customer=customer, status="S", datetime__lt=dt)
        total_old_price = sum([sale.price * sale.amount for sale in old_sales])
        new_sales = Sale.objects.filter(salelist = obj, status="S")
        total_new_price = sum([sale.price * sale.amount for sale in new_sales])
        total_new_debt = total_old_price + total_new_price - self.get_total_paid_amount(obj)
        if self.get_old_debt(obj) == 0:
            if total_new_debt > 0:
                return total_new_debt
            return 0
        return total_new_price

    def get_total_paid_amount(self, obj):
        customer = obj.salelist_sales.first().customer
        payments = Payment.objects.filter(customer = customer)
        return sum([payment.amount for payment in payments])
    
    def get_paid_amount(self, obj):
        customer = obj.salelist_sales.first().customer
        old_sales = Sale.objects.filter(customer=customer, status="S", datetime__lt=dt)
        total_old_price = sum([sale.price * sale.amount for sale in old_sales])
        total_payment_amount = sum([payment for payment in Payment.objects.filter(customer = customer)])
        paid_amount = total_payment_amount - total_old_price
        return paid_amount if paid_amount > 0 else 0

    def get_total_debt(self, obj):
        customer = obj.salelist_sales.first().customer
        sales = Sale.objects.filter(customer=customer, status="S")
        total_price = sum([sale.price * sale.amount for sale in sales])
        return total_price - self.get_total_paid_amount(obj)
    
    def get_total_profit(self, obj):
        price = sum([sale.price * sale.amount for sale in obj.salelist_sales.filter(status="S")])
        cost_price = sum([sale.product.cost_price * sale.amount for sale in obj.salelist_sales.filter(status="S")])
        return price - cost_price

class SaleListDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleList
        fields = "__all__"

class SaleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"

class SaleListUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(allow_blank=True)
    dt = serializers.DateTimeField(allow_null=True) # datetime
    
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

class BulkPurchaseSerializer(serializers.Serializer):
    supplier = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.CharField()
    currency = serializers.CharField()
    products = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    amounts = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    purchase_prices = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
    cost_prices = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
    prices = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
    discount_prices = serializers.ListField(child=serializers.FloatField(), allow_empty=False)


class BulkSaleSerializer(serializers.Serializer):
    customer = serializers.IntegerField()
    products = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    prices = serializers.ListField(child=serializers.FloatField(), allow_empty=False)
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

class SupplierPaymentSerializer(serializers.ModelSerializer):
    supplier = CustomUserSerializer()
    class Meta:
        model = SupplierPayment
        fields = "__all__"

class SupplierPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierPayment
        fields = "__all__"