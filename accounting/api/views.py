from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from accounting.models import PurchaseList, Purchase, Stock, SaleList, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense, SupplierPayment
from accounting.api.serializers import (
    PurchaseCreateSerializer, PurchaseSerializer, PurchaseListSerializer, PurchaseListRetrieveSerializer,
    AddToStockSerializer, StockSerializer, StockUpdateSerializer, SaleSerializer, SaleListSerializer,
    SaleListRetrieveSerializer, SaleCreateSerializer, PaymentSerializer, PaymentCreateSerializer, ProductActionSerializer,
    CustomerActionSerializer, BulkPurchaseSerializer, BulkSaleSerializer, ReturnBackSerializer, ReturnBackCreateSerializer,
    ExpenseSerializer, SupplierPaymentSerializer, SupplierPaymentCreateSerializer
)
from core.models import Product, CustomUser
from core.api.serializers import ProductSerializer, ProductUpdateSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
import datetime

class PurchaseCreateAPIView(CreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseCreateSerializer

    def create(self, request, *args, **kwargs):
        purchase_data = {
            "supplier": request.data.get("supplier"),
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
            product.currency = product_data["currency"] if product_data["currency"] else product.currency
            product.amount = product.amount + int(purchase_data["amount"])
            product.save()

            stock_status = serializer.data.get("status")
            if stock_status == "A":
                stock, created = Stock.objects.get_or_create(
                    product = product
                )
                stock.amount = stock.amount + int(purchase_data["amount"])
                stock.save()

                dt_data = purchase_data["date"].split("-")
                ProductAction.objects.create(
                    product = product,
                    date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                    incoming_product_number = int(purchase_data["amount"]),
                    remaining_product_number = stock.amount
                )

            response_data = {
                "message": f"{int(purchase_data['amount'])} Məhsul alındı: {product.name}"
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
            previous_instance_status = instance.status
            serializer.save()
            instance.product.amount = instance.product.amount - previous_instance_amount + instance.amount
            instance.product.save()

            if previous_instance_status == "G" and instance.status == "A":
                stock, created = Stock.objects.get_or_create(
                    product = instance.product
                )
                stock.amount = stock.amount + instance.amount
                stock.save()
                dt_data = purchase_data["date"].split("-")
                ProductAction.objects.create(
                    product = instance.product,
                    date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                    incoming_product_number = int(purchase_data["amount"]),
                    remaining_product_number = stock.amount
                )
            elif previous_instance_status == "A" and instance.status == "G":
                stock = Stock.objects.get(
                    product = instance.product
                )
                stock.amount = stock.amount - previous_instance_amount
                stock.save()
            elif previous_instance_status == "A" and instance.status == "A":
                stock = Stock.objects.get(
                    product = instance.product
                )
                stock.amount = stock.amount - previous_instance_amount + instance.amount
                stock.save()
            # pr_serializer = ProductUpdateSerializer(instance.product, data=product_data, partial=True)
            # print(type(instance.product))
            # print(pr_serializer.is_valid())
            # if pr_serializer.is_valid():
            #     print(pr_serializer.data)
            #     pr_serializer.save()
            # else:
            #     return Response(pr_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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

class PurchaseListListAPIView(ListAPIView):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListSerializer

class PurchaseListRetrieveAPIView(RetrieveAPIView):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListRetrieveSerializer
    lookup_field = "id"

class BulkPurchaseAPIView(APIView):
    def post(self, request):
        serializer = BulkPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            supplier_id = serializer.validated_data.get("supplier")
            date = serializer.validated_data.get("date")
            p_status = serializer.validated_data.get("status")
            currency = serializer.validated_data.get("currency")
            products = serializer.validated_data.get("products")
            amounts = serializer.validated_data.get("amounts")
            purchase_prices = serializer.validated_data.get("purchase_prices")
            cost_prices = serializer.validated_data.get("cost_prices")
            prices = serializer.validated_data.get("prices")
            discount_prices = serializer.validated_data.get("discount_prices")

            purchaselist = PurchaseList.objects.create(currency=currency)
            supplier = get_object_or_404(CustomUser, id=supplier_id)

            for i in range(len(products)):
                product = get_object_or_404(Product, id=products[i])
                Purchase.objects.create(
                    supplier = supplier,
                    product = product,
                    purchaselist = purchaselist,
                    amount = amounts[i],
                    date = date,
                    status = p_status,
                )
                product.purchase_price = purchase_prices[i]
                product.cost_price = cost_prices[i]
                product.price = prices[i]
                product.discount_price = discount_prices[i]
                product.currency = currency
                product.amount = product.amount + amounts[i]
                product.save()

                if p_status == "A":
                    stock, created = Stock.objects.get_or_create(
                        product = product
                    )
                    stock.amount = stock.amount + amounts[i]
                    stock.save()

                    ProductAction.objects.create(
                        product = product,
                        date = date,
                        incoming_product_number = amounts[i],
                        remaining_product_number = stock.amount
                    )

            response_data = {
                "message": f"{len(products)} məhsul alışı icra edildi."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockListAPIView(ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class AddToStockAPIView(APIView):
    def post(self, request):
        serializer = AddToStockSerializer(data=request.data)

        if serializer.is_valid():
            item_ids = serializer.validated_data["item_ids"]
            items = Purchase.objects.filter(id__in=item_ids)
            for item in items:
                stock, created = Stock.objects.get_or_create(
                    product = item.product
                )
                stock.amount = stock.amount + item.amount
                stock.save()
                item.status = "A"
                item.save()
            response_data = {
                "message": f"{len(items)} məhsul anbara əlavə edildi."
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StockRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockUpdateSerializer
    lookup_field = "id"
    
class SaleListAPIView(ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class SaleListListAPIView(ListAPIView):
    queryset = SaleList.objects.all()
    serializer_class = SaleListSerializer

class SaleListRetrieveAPIView(RetrieveAPIView):
    queryset = SaleList.objects.all()
    serializer_class = SaleListRetrieveSerializer
    lookup_field = "id"

class SaleCreateAPIView(CreateAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleCreateSerializer

    def create(self, request, *args, **kwargs):
       sale_data = {
           "seller": request.user.id,
           "product": request.data.get("product"),
           "customer": request.data.get("customer"),
           "amount": request.data.get("amount"),
           "datetime": request.data.get("datetime"),
           "price": request.data.get("price"),
           "status": request.data.get("status")
        }
       serializer = self.get_serializer(data=sale_data)
       if serializer.is_valid():
            serializer.save()
            product = Product.objects.get(id=sale_data["product"])
            product.amount = product.amount - int(sale_data["amount"])
            product.save()
            if hasattr(product, "stock"):
                product.stock.amount = product.stock.amount - int(sale_data["amount"])
                product.stock.save()
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
            previous_instance_status = instance.status
            serializer.save()

            if previous_instance_status == "G" and instance.status == "S":
                instance.product.amount = instance.product.amount - instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount - instance.amount
                    instance.product.stock.save()
            elif previous_instance_status == "S" and instance.status == "G":
                instance.product.amount = instance.product.amount + instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount + instance.amount
                    instance.product.stock.save()
            elif previous_instance_status == "S" and instance.status == "S":
                instance.product.amount = instance.product.amount + previous_instance_amount - instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount + previous_instance_amount - instance.amount
                    instance.product.stock.save()
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
            statuses = serializer.validated_data["statuses"]

            seller = request.user
            customer = CustomUser.objects.get(id=customer_id)
            salelist = SaleList.objects.create()

            for i in range(len(products_id)):
                product = get_object_or_404(Product, id=products_id[i])
                sale = Sale.objects.create(
                    seller = seller,
                    customer = customer,
                    salelist = salelist,
                    product = product,
                    amount = amounts[i],
                    datetime = datetimes[i],
                    price = prices[i],
                    status = statuses[i]
                )
                if sale.status == "S":
                    product.amount = product.amount - amounts[i]
                    product.save()
                    if hasattr(product, "stock"):
                        product.stock.amount = product.stock.amount - amounts[i]
                        product.stock.save()
                ProductAction.objects.create(
                    product = product,
                    customer = customer,
                    date = datetimes[i].date(), 
                    sold_product_number = amounts[i],
                    remaining_product_number = product.amount
                )
                CustomerAction.objects.create(
                    customer = customer,
                    product = product,
                    date = datetimes[i].date(), 
                    product_price = prices[i]
                )
            response_data = {
                "message": f"Seçilmiş məhsullar '{customer}' müştəriyə satıldı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            customer_debt = sum([sale.price * sale.amount for sale in customer.customer_sales.all()])
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
            instance = serializer.save()
            amount = request.data.get("amount")
            rb_status = instance.status # returnback status
            sale = instance.sale
            sale_amount = sale.amount - int(amount)
            sale.amount = sale_amount
            sale.save()
            if rb_status == "I":
                sale.product.amount = sale.product.amount + instance.amount
                sale.product.save()
                if hasattr(sale.product, "stock"):
                    sale.product.stock.amount = sale.product.stock.amount + instance.amount
                    sale.product.stock.save()
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            previous_instance_amount = instance.amount
            previous_instance_status = instance.status
            serializer.save()
            instance.sale.amount = instance.sale.amount + previous_instance_amount - instance.amount
            instance.sale.save()
            if previous_instance_status == "Y" and instance.status == "I":
                instance.sale.product.amount = instance.sale.product.amount + instance.amount
                instance.sale.product.save()
                if hasattr(instance.sale.product, "stock"):
                    instance.sale.product.stock.amount = instance.sale.product.stock.amount + instance.amount
                    instance.sale.product.stock.save()
            elif previous_instance_status == "I" and instance.status == "Y":
                instance.sale.product.amount = instance.sale.product.amount - instance.amount
                instance.sale.product.save()
                if hasattr(instance.sale.product, "stock"):
                    instance.sale.product.stock.amount = instance.sale.product.stock.amount - instance.amount
                    instance.sale.product.stock.save()
            elif previous_instance_status == "I" and instance.status == "I":
                instance.sale.product.amount = instance.sale.product.amount - previous_instance_amount + instance.amount
                instance.sale.product.save()
                if hasattr(instance.sale.product, "stock"):
                    instance.sale.product.stock.amount = instance.sale.product.stock.amount - previous_instance_amount + instance.amount
                    instance.sale.product.stock.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class DashboardAPIView(APIView):
    def get(self, request, seller_id, month, year):
        user = get_object_or_404(CustomUser, id=seller_id)
        months = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr", "All"]
        try:
            m = months.index(month) + 1
        except ValueError as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        if m < 13:
            sales = Sale.objects.filter(
                datetime__month = m, datetime__year = year, status = "S"
            )
            payments = Payment.objects.filter(
                datetime__month = m, datetime__year = year
            )
            expenses = Expense.objects.filter(
                date__month = m, date__year = year
            )
            returnbacks = ReturnBack.objects.filter(
                date__month = m, date__year = year
            )
            supplierpayments = SupplierPayment.objects.filter(
                datetime__month = m, datetime__year = year
            )
        else:
            sales = Sale.objects.filter(
                datetime__year = year, status = "S"
            )
            payments = Payment.objects.filter(
                datetime__year = year
            )
            expenses = Expense.objects.filter(
                date__year = year
            )
            returnbacks = ReturnBack.objects.filter(
                date__year = year
            )
            supplierpayments = SupplierPayment.objects.filter(
                datetime__year = year
            )
        if user.is_superuser:
            total_income = sum([payment.amount for payment in payments])
            total_outcome = sum([expense.amount for expense in expenses])
            total_returnback = sum([returnback.amount * returnback.sale.price for returnback in returnbacks])
            total_m_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="M")])
            total_d_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="D")])
            total_r_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="R")])
        else:
            sales = sales.filter(seller=user)
            total_income = None
            total_outcome = None
            total_returnback = None
            total_m_supplierpayments = None
            total_d_supplierpayments = None
            total_r_supplierpayments = None
        sold_product_number = sum([sale.amount for sale in sales])
        customer_number = sales.values('customer').distinct().count()
        total_sale_amount = sum([sale.price * sale.amount for sale in sales])
        total_cost_amount = sum([sale.product.cost_price * sale.amount for sale in sales])
        dashboard_data = {
            "sold_product_number": sold_product_number,
            "customer_number": customer_number,
            "total_sale_amount": total_sale_amount,
            "total_income": total_income,
            "total_outcome": total_outcome,
            "total_returnback": total_returnback,
            "total_cost_amount": total_cost_amount,
            "total_supplier_m_payment_amount": total_m_supplierpayments,
            "total_supplier_d_payment_amount": total_d_supplierpayments,
            "total_supplier_r_payment_amount": total_r_supplierpayments
        }
        return Response(dashboard_data, status=status.HTTP_200_OK)
    permission_classes = (IsAdminUser,)
    
class SaleDynamicsAPIView(APIView):
    def get(self, request, seller_id, filter_data, brand_id):
        user = get_object_or_404(CustomUser, id=seller_id)
        if filter_data == "A":
            months = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "İyun", "İyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
            total_sale_amounts = []
            if user.is_superuser:
                for i in range(len(months)):
                    year = datetime.datetime.now().year
                    if brand_id:
                        sales = Sale.objects.filter(
                            product__brand__id = brand_id,
                            datetime__date__month = i + 1,
                            datetime__date__year = year,
                            status = "S"
                        )
                    else:
                        sales = Sale.objects.filter(
                            datetime__date__month = i + 1,
                            datetime__date__year = year,
                            status = "S"
                        )
                    total_sale_amount = sum([sale.price * sale.amount for sale in sales])
                    total_sale_amounts.append(total_sale_amount)
            else:
                for i in range(len(months)):
                    year = datetime.datetime.now().year
                    if brand_id:
                        sales = Sale.objects.filter(
                            seller = user,
                            product__brand__id = brand_id,
                            datetime__date__month = i + 1,
                            datetime__date__year = year,
                            status = "S"
                        )
                    else:
                        sales = Sale.objects.filter(
                            seller = user,
                            datetime__date__month = i + 1,
                            datetime__date__year = year,
                            status = "S"
                        )
                    total_sale_amount = sum([sale.price * sale.amount for sale in sales])
                    total_sale_amounts.append(total_sale_amount)
            response_data = {
                month: amount for (month, amount) in zip(months, total_sale_amounts)
            }
            return Response(response_data, status=status.HTTP_200_OK)
        elif filter_data == "I":
            if user.is_superuser:
                all_sale_years = [sale.datetime.year for sale in Sale.objects.all()]
                all_sale_years = list(set(all_sale_years))
                all_sale_years.sort()
                total_sale_amounts = []
                for year in all_sale_years:
                    if brand_id:
                        sales = Sale.objects.filter(
                            product__brand__id = brand_id,
                            datetime__date__year = year,
                            status = "S"
                        )
                    else:
                        sales = Sale.objects.filter(
                            datetime__date__year = year,
                            status = "S"
                        )
                    total_sale_amount = sum([sale.price * sale.amount for sale in sales])
                    total_sale_amounts.append(total_sale_amount)
            else:
                all_sale_years = [sale.datetime.year for sale in Sale.objects.filter(seller=user)]
                all_sale_years = list(set(all_sale_years))
                all_sale_years.sort()
                total_sale_amounts = []
                for year in all_sale_years:
                    if brand_id:
                        sales = Sale.objects.filter(
                            seller = user,
                            product__brand__id = brand_id,
                            datetime__date__year = year,
                            status = "S"
                        )
                    else:
                        sales = Sale.objects.filter(
                            seller = user,
                            datetime__date__year = year,
                            status = "S"
                        )
                    total_sale_amount = sum([sale.price * sale.amount for sale in sales])
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
            customer_debt = sum([sale.price * sale.amount for sale in customer.customer_sales.all()]) - sum([payment.amount for payment in customer.payments.all()])
            customer_debts.append(customer_debt)
        
        indebted_customers = list(zip(customers, customer_debts))
        indebted_customers.sort(reverse=True, key=lambda x: x[1])
        most_indebted_customers = indebted_customers[:5]
        customers_data = []
        for customer in most_indebted_customers:
            customer_data = {
                "name": customer[0].username,
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

class SupplierPaymentListAPIView(ListAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentSerializer

class SupplierPaymentCreateAPIView(CreateAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentCreateSerializer
    
class SupplierPaymentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentCreateSerializer
    lookup_field = "id"