from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
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
from core.api.serializers import ProductSerializer
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
    
class PurchaseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseCreateSerializer
    lookup_field = "id" 

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            previous_instance_amount = instance.amount
            serializer.save()
            instance.product.amount = instance.product.amount - previous_instance_amount + instance.amount
            instance.product.save()
            # productaction = instance.product_actions.all()
            # productaction.product = instance.product
            # productaction.date = instance.datetime.date()
            # productaction.incoming_product_number = instance.amount
            # productaction.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
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
    
class SaleRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleCreateSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            previous_instance_amount = instance.amount
            serializer.save()
            instance.product.amount = instance.product.amount + previous_instance_amount - instance.amount
            instance.product.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
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
    
class PaymentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentCreateSerializer
    lookup_field = "id"

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
            ProductAction.objects.create(
                product = sale.product,
                customer = sale.customer,
                date = request.data.get("date"),
                return_product_number = amount
            )
            CustomerAction.objects.create(
                customer = sale.customer,
                product = sale.product,
                date = request.data.get("date"),
                product_price = sale.price,
                return_amount = sale.price
            )
            response_data = {
                "message": f"{amount} ədəd '{sale.product.name}' məhsulu geri qaytarıldı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ReturnBackRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = ReturnBack.objects.all()
    serializer_class = ReturnBackCreateSerializer
    lookup_field = "id" 

class ExpenseListAPIView(ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseCreateAPIView(CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    lookup_field = "id"

class InvoiceListAPIView(ListAPIView):
    def get_queryset(self):
        customer_id = self.kwargs.get("id")
        customer = get_object_or_404(CustomUser, id=customer_id)
        return Sale.objects.filter(customer=customer)
    serializer_class = SaleSerializer

class DashbordAPIView(APIView):
    def get(self, request):
        sold_product_number = sum([sale.amount for sale in Sale.objects.all()])
        customer_number = len(CustomUser.objects.filter(is_staff=False))
        total_sale_amount = sum([sale.price for sale in Sale.objects.all()])
        total_income = sum([payment.amount for payment in Payment.objects.all()])
        dashboard_data = {
            "sold_product_number": sold_product_number,
            "customer_number": customer_number,
            "total_sale_amount": total_sale_amount,
            "total_income": total_income
        }
        return Response(dashboard_data, status=status.HTTP_200_OK)
    
class SaleDynamicsAPIView(APIView):
    def get(self, request, filter_data):
        # filter_data = self.kwargs.get("my_filter_data")
        if filter_data == "A":
            months = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "İyun", "İyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
            total_sale_amounts = []
            for i in range(len(months)):
                year = datetime.datetime.now().year
                total_sale_amount = sum([sale.price for sale in Sale.objects.filter(
                    datetime__date__month = i + 1,
                    datetime__date__year = year
                )])
                total_sale_amounts.append(total_sale_amount)
            response_data = {
                month: amount for (month, amount) in zip(months, total_sale_amounts)
            }
            return Response(response_data, status=status.HTTP_200_OK)
        elif filter_data == "I":
            all_sale_years = [sale.datetime.year for sale in Sale.objects.all()]
            all_sale_years = list(set(all_sale_years))
            all_sale_years.sort()
            total_sale_amounts = []
            for year in all_sale_years:
                total_sale_amount = sum([sale.price for sale in Sale.objects.filter(
                    datetime__year = year
                )])
                total_sale_amounts.append(total_sale_amount)
            response_data = {
                year: amount for (year, amount) in zip(all_sale_years, total_sale_amounts)
            }
            return Response(response_data, status = status.HTTP_200_OK)
        else:
            response_data = {
                "errors": "Göndərilən məlumat doğru deyil."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
class MostInDebtedCustomerAPIView(APIView):
    def get(self, request):
        customers = CustomUser.objects.all()
        customer_debts = []
        for customer in customers:
            customer_debt = sum([sale.price for sale in customer.customer_sales.all()]) - sum([payment.amount for payment in customer.payments.all()])
            customer_debts.append(customer_debt)
        
        indebted_customers = list(zip(customers, customer_debts))
        indebted_customers.sort(reverse=True, key=lambda x: x[1])
        most_indebted_customers = indebted_customers[:5]
        customers_data = []
        for customer in most_indebted_customers:
            customer_data = {
                "name": customer[0].first_name + " " + customer[0].last_name,
                "debt": customer[1],
                "phone_number": customer[0].phone_number
            }
            customers_data.append(customer_data)
        response_data = {"most_indebted_customers": customers_data}
        return Response(response_data, status=status.HTTP_200_OK)
    
class StockOutProductsListAPIView(ListAPIView):
    def get_queryset(self):
        return Product.objects.filter(amount__lte=10)
    serializer_class = ProductSerializer
            