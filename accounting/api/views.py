from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounting.models import Purchase, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense
from accounting.api.serializers import (
    PurchaseCreateSerializer, PurchaseSerializer, AddToStockSerializer, SaleSerializer, 
    SaleCreateSerializer, PaymentSerializer, PaymentCreateSerializer, ProductActionSerializer,
    CustomerActionSerializer, BulkSaleSerializer, ReturnBackSerializer, ReturnBackCreateSerializer,
    ExpenseSerializer
)
from core.models import Product, CustomUser
from django.shortcuts import get_object_or_404
import datetime

class PurchaseCreateAPIView(CreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseCreateSerializer

    def create(self, request, *args, **kwargs):
        purchase_data = {
            "product": request.data.get("product"),
            "amount": request.data.get("amount"),
            "date": request.data.get("date"),
            "status": request.data.get("status")
        }

        product_data = {
            "cost_price": request.data.get("cost_price"),
            "purchase_price": request.data.get("purchase_price"),
            "price": request.data.get("price"),
            "discount_price": request.data.get("discount_price"),
            "currency": request.data.get("currency")
        }

        serializer = self.get_serializer(data=purchase_data)
        if serializer.is_valid():
            serializer.save()
            product = Product.objects.get(id=purchase_data["product"])
            product.cost_price = product_data["cost_price"]
            product.purchase_price = product_data["purchase_price"]
            product.price = product_data["price"]
            product.discount_price = product_data["discount_price"]
            product.currency = product_data["currency"]
            product.amount = product.amount + int(purchase_data["amount"])
            product.save()

            dt_data = purchase_data["date"].split("-")
            ProductAction.objects.create(
               product = product,
               date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
               incoming_product_number = int(purchase_data["amount"])
            )

            response_data = {
                "message": "Məhsul alındı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseListAPIView(ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class StockListAPIView(ListAPIView):
    def get_queryset(self):
        return Purchase.objects.filter(
            status = 'A'
        )
    serializer_class = PurchaseSerializer

class AddToStockAPIView(APIView):
    def post(self, request):
        serializer = AddToStockSerializer(data=request.data)

        if serializer.is_valid():
            item_ids = serializer.validated_data["item_ids"]
            items = Purchase.objects.filter(id__in=item_ids)
            items.update(in_stock=True)
            items.update(status='A')

            response_data = {
                "message": f"{len(items)} məhsul anbara əlavə edildi."
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SaleListAPIView(ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class SaleCreateAPIView(CreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleCreateSerializer

    def create(self, request, *args, **kwargs):
       sale_data = {
           "product": request.data.get("product"),
           "customer": request.data.get("customer"),
           "amount": request.data.get("amount"),
           "datetime": request.data.get("datetime"),
           "price": request.data.get("price")
       }
       serializer = self.get_serializer(data=sale_data)
       if serializer.is_valid():
            serializer.save()
            product = Product.objects.get(id=sale_data["product"])
            product.amount = product.amount - int(sale_data["amount"])
            product.save()
            customer = CustomUser.objects.get(id=sale_data["customer"])
            dt = sale_data["datetime"].split("T")[0]
            dt_data = dt.split("-")
            ProductAction.objects.create(
               product = product,
               customer = customer,
               date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
            #    incoming_product_number = product.amount,
               sold_product_number = sale_data["amount"],
               remaining_product_number = product.amount     
            )
            CustomerAction.objects.create(
                customer = customer,
                product = product,
                date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))), 
                product_price = sale_data["price"]
            )
            response_data = {"message": "Satış edildi."}
            return Response(response_data, status=status.HTTP_201_CREATED)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BulkSaleAPIView(APIView):
    def post(self, request):
        serializer = BulkSaleSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data["customer"]
            products_id = serializer.validated_data["products"]
            prices = serializer.validated_data["prices"]
            amounts = serializer.validated_data["amounts"]
            datetimes = serializer.validated_data["datetimes"]

            customer = CustomUser.objects.get(id=customer_id)
            products = Product.objects.filter(id__in=products_id)
            print(products)

            for i in range(len(products)):
                Sale.objects.create(
                    customer = customer,
                    product = products[i],
                    amount = amounts[i],
                    datetime = datetimes[i],
                    price = prices[i]
                )
                products[i].amount = products[i].amount - amounts[i]
                products[i].save()
                ProductAction.objects.create(
                    product = products[i],
                    customer = customer,
                    date = datetimes[i].date(), 
                    sold_product_number = amounts[i],
                    remaining_product_number = products[i].amount
                )
                CustomerAction.objects.create(
                    customer = customer,
                    product = products[i],
                    date = datetimes[i].date(), 
                    product_price = prices[i]
                )
            response_data = {
                "message": f"Seçilmiş məhsullar '{customer}' müştəriyə satıldı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentCreateAPIView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        payment_data = {
            "customer": request.data.get("customer"),
            "datetime": request.data.get("datetime"),
            "amount": request.data.get("amount")
        }
        serializer = self.get_serializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            customer = CustomUser.objects.get(id=payment_data["customer"])
            customer_debt = sum([sale.price for sale in customer.customer_sales.all()])
            previous_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.all()]
            previous_total_amount = 0 if not previous_amounts else sum(previous_amounts, start=0)
            dt = payment_data["datetime"].split("T")[0]
            dt_data = dt.split("-")
            CustomerAction.objects.create(
                customer = customer,
                date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                payment_amount = payment_data["amount"],
                total_amount = previous_total_amount + int(payment_data["amount"]),
                remaining_amount = customer_debt - previous_total_amount - int(payment_data["amount"]),
            )

            response_data = {
                "message": "Ödəniş əlavə olundu."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductActionListAPIView(ListAPIView):
    def get_queryset(self):
        product_id = self.kwargs.get("id")
        product = get_object_or_404(Product, id=product_id)
        return ProductAction.objects.filter(
            product = product
        )
    serializer_class = ProductActionSerializer

class CustomerActionListAPIView(ListAPIView):
    def get_queryset(self):
        customer_id = self.kwargs.get("id")
        customer = get_object_or_404(CustomUser, id=customer_id)
        return CustomerAction.objects.filter(
            customer = customer
        )
    serializer_class = CustomerActionSerializer

class ReturnBackListAPIView(ListAPIView):
    queryset = ReturnBack.objects.all()
    serializer_class = ReturnBackSerializer

class ReturnBackCreateAPIView(CreateAPIView):
    queryset = ReturnBack.objects.all()
    serializer_class = ReturnBackCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            sale_id = request.data.get("sale")
            amount = request.data.get("amount")
            sale = get_object_or_404(Sale, id=sale_id)
            sale_amount = sale.amount - int(amount)
            sale.amount = sale_amount
            sale.save()
            response_data = {
                "message": f"{amount} ədəd '{sale.product.name}' məhsulu geri qaytarıldı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseListAPIView(ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseCreateAPIView(CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class InvoiceListAPIView(ListAPIView):
    def get_queryset(self):
        customer_id = self.kwargs.get("id")
        customer = get_object_or_404(CustomUser, id=customer_id)
        return Sale.objects.filter(customer=customer)
    serializer_class = SaleSerializer

