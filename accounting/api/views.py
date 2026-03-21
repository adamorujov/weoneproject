from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from accounting.models import PurchaseList, Purchase, Stock, SaleList, Sale, Payment, ProductAction, CustomerAction, ReturnBack, Expense, SupplierPayment, CustomerActionList
from accounting.api.serializers import (
    PurchaseCreateSerializer, PurchaseSerializer, PurchaseListSerializer, PurchaseListRetrieveSerializer, PurchaseListUpdateSerializer,
    PurchaseListDestroySerializer, AddToStockSerializer, StockSerializer, StockUpdateSerializer, SaleSerializer, 
    SaleListSerializer, SaleListRetrieveSerializer, SaleListDestroySerializer, SaleCreateSerializer, SaleListUpdateSerializer, PaymentSerializer, 
    PaymentCreateSerializer, ProductActionSerializer, CustomerActionSerializer, BulkPurchaseSerializer, BulkSaleSerializer, 
    ReturnBackSerializer, ReturnBackCreateSerializer, ExpenseSerializer, SupplierPaymentSerializer, SupplierPaymentCreateSerializer,
    CustomerActionListSerializer, ShortSaleSerializer
)
from core.models import Product, CustomUser
from core.api.serializers import ProductSerializer, ProductUpdateSerializer, CustomUserSerializer
from django.shortcuts import get_object_or_404
import datetime
from django.utils import timezone
from decimal import Decimal

from rest_framework.filters import BaseFilterBackend

class TotalDebtFilterBackend(BaseFilterBackend):
    """
    Filter queryset by min_total_debt and max_total_debt query params.
    """
    def filter_queryset(self, request, queryset, view):
        min_amount = request.query_params.get('min_total_amount')
        max_amount = request.query_params.get('max_total_amount')

        if not min_amount and not max_amount:
            return queryset

        # convert to float
        if min_amount:
            min_amount = float(min_amount)
        if max_amount:
            max_amount = float(max_amount)

        # filter manually because total_debt is Python property
        filtered = []
        for sale in queryset:
            amount = sale.total_amount
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue
            filtered.append(sale)

        return filtered
    
class PurchaseDateFilterBackend(BaseFilterBackend):
    """
    Filter queryset by min_total_debt and max_total_debt query params.
    """
    def filter_queryset(self, request, queryset, view):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date and not end_date:
            return queryset

        # convert to float
        if start_date:
            st_dt = start_date.split("-")
            start_date = datetime.date(int(st_dt[0]), int(st_dt[1]), int(st_dt[2]))
        if end_date:
            e_dt = end_date.split("-")
            end_date = datetime.date(int(e_dt[0]), int(e_dt[1]), int(e_dt[2]))

        # filter manually because total_debt is Python property
        filtered = []
        for purchaselist in queryset:
            if not purchaselist.purchaselist_purchases.exists():
                continue
            p_date = purchaselist.purchaselist_purchases.first().date
            if start_date is not None and p_date < start_date:
                continue
            if end_date is not None and p_date > end_date:
                continue
            filtered.append(purchaselist)

        return filtered
    
class SaleDateFilterBackend(BaseFilterBackend):
    """
    Filter queryset by min_total_debt and max_total_debt query params.
    """
    def filter_queryset(self, request, queryset, view):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date and not end_date:
            return queryset

        # convert to float
        if start_date:
            st_dt = start_date.split("-")
            start_date = datetime.date(int(st_dt[0]), int(st_dt[1]), int(st_dt[2]))
        if end_date:
            e_dt = end_date.split("-")
            end_date = datetime.date(int(e_dt[0]), int(e_dt[1]), int(e_dt[2]))

        # filter manually because total_debt is Python property
        filtered = []
        for salelist in queryset:
            if not salelist.salelist_sales.exists():
                continue
            dt = salelist.salelist_sales.first().datetime.date()
            if start_date is not None and dt < start_date:
                continue
            if end_date is not None and dt > end_date:
                continue
            filtered.append(salelist)

        return filtered

class CustomPagination(PageNumberPagination):
    page_size = 10  # default olaraq hər səhifədə 10 obyekt
    page_size_query_param = 'page_size'  # istifadəçi ?page_size=20 yaza bilər
    max_page_size = 100  # maksimum icazə verilən ölçü

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
            # product.amount = product.amount + int(purchase_data["amount"])
            product.save()

            stock_status = serializer.data.get("status")
            if stock_status == "A":
                stock, created = Stock.objects.get_or_create(
                    product = product
                )
                product.amount = product.amount + int(purchase_data["amount"])
                stock.amount = stock.amount + int(purchase_data["amount"])
                stock.save()

                # dt_data = purchase_data["date"].split("-")
                # ProductAction.objects.create(
                #     product = product,
                #     date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                #     incoming_product_number = int(purchase_data["amount"]),
                #     remaining_product_number = stock.amount
                # )

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
            instance.product.purchase_price = instance.price
            instance.product.save()
            # instance.product.amount = instance.product.amount - previous_instance_amount + instance.amount
            # instance.product.save()
            customeractionlist = CustomerActionList.objects.create()

            if previous_instance_status == "G" and instance.status == "A":
                stock, created = Stock.objects.get_or_create(
                    product = instance.product
                )

                stock.amount = stock.amount + instance.amount
                stock.save()

                ProductAction.objects.create(
                    product = instance.product,
                    date = instance.date,
                    incoming_product_number = instance.amount,
                    remaining_product_number = stock.amount,
                    action = "Anbara əlavə edildi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.supplier,
                    product = instance.product,
                    date = instance.date,
                    product_price = instance.price * instance.amount,
                    action = "Məhsul alışı icra edildi"
                )
            elif previous_instance_status == "A" and instance.status == "G":
                stock = Stock.objects.get(
                    product = instance.product
                )
                stock.amount = stock.amount - previous_instance_amount
                stock.save()
                ProductAction.objects.create(
                    product = instance.product,
                    date = instance.date,
                    remaining_product_number = stock.amount,
                    action = "Anbardan silindi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.supplier,
                    product = instance.product,
                    date = instance.date,
                    product_price = instance.price * instance.amount,
                    action = "Məhsul alışı ləğv edildi"
                )
            elif previous_instance_status == "A" and instance.status == "A":
                stock = Stock.objects.get(
                    product = instance.product
                )
                stock.amount = stock.amount - previous_instance_amount + instance.amount
                stock.save()
                ProductAction.objects.create(
                    product = instance.product,
                    date = instance.date,
                    incoming_product_number = instance.amount - previous_instance_amount,
                    remaining_product_number = stock.amount,
                    action = "Anbara əlavə edildi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.supplier,
                    product = instance.product,
                    date = instance.date,
                    product_price = instance.price * (instance.amount - previous_instance_amount),
                    action = "Məhsul alışı əlavə edildi"
                )
                
            instance.product.amount = instance.product.stock.amount
            instance.product.save()
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

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'A':
            instance.product.stock.amount = instance.product.stock.amount - instance.amount
            customeractionlist = CustomerActionList.objects.create()
            if instance.product.stock.amount > 0:
                instance.product.stock.save()
                instance.product.amount = instance.product.stock.amount
                instance.product.save()
                ProductAction.objects.create(
                    product = instance.product,
                    date = instance.date,
                    remaining_product_number = instance.product.stock.amount,
                    action = "Anbardan silindi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.supplier,
                    product = instance.product,
                    date = instance.date,
                    product_price = instance.price * instance.amount,
                    action = "Məhsul alışı ləğv edildi"
                )
            else:
                instance.product.stock.delete()
                instance.product.amount = 0
                instance.product.save()
                ProductAction.objects.create(
                    product = instance.product,
                    date = instance.date,
                    remaining_product_number = 0,
                    action = "Anbardan silindi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.supplier,
                    product = instance.product,
                    date = instance.date,
                    product_price = instance.price * instance.amount,
                    action = "Məhsul alışı ləğv edildi"
                )
        return super().delete(request, *args, **kwargs)

class PurchaseListAPIView(ListAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["product__name", "product__degree", "product__articles__name", "product__brand__name", "product__store__name", "product__category__name"]

from django.db.models import Max
class PurchaseListListAPIView(ListAPIView):
    def get_queryset(self):
        return PurchaseList.objects.annotate(
                date=Max("purchaselist_purchases__date")
            ).order_by("-date")
    serializer_class = PurchaseListSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, PurchaseDateFilterBackend]
    search_fields = ["purchaselist_purchases__supplier__username", "purchaselist_purchases__supplier__first_name", "purchaselist_purchases__supplier__last_name"]

class PurchaseListRetrieveAPIView(RetrieveAPIView):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListRetrieveSerializer
    lookup_field = "id"

class PurchaseListUpdateAPIView(UpdateAPIView):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListUpdateSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            supplier_id = serializer.validated_data.get("supplier_id")
            currency = serializer.validated_data.get("currency")
            p_status = serializer.validated_data.get("status")
            date = serializer.validated_data.get("date")
            purchases = instance.purchaselist_purchases.all()
            customeractionlist = CustomerActionList.objects.create()
            if supplier_id:
                supplier = get_object_or_404(CustomUser, id=supplier_id)
                for purchase in purchases:
                    purchase.supplier = supplier
                    purchase.save()
            if currency:
                instance.currency = currency
                instance.save()
            if p_status:
                for purchase in purchases:
                    if purchase.status == 'A' and p_status == 'G':
                        purchase.status = 'G'
                        purchase.save()
                        purchase.product.stock.amount = purchase.product.stock.amount - purchase.amount
                        if purchase.product.stock.amount > 0:
                            purchase.product.stock.save()
                            purchase.product.amount = purchase.product.stock.amount
                            purchase.product.save()
                        else:
                            purchase.product.stock.delete()
                            purchase.product.amount = 0
                            purchase.product.save()

                        # if customeractionlist.id is not None:

                        #     customeractionlist.delete() 

                        ProductAction.objects.create(
                            product = purchase.product,
                            date = purchase.date,
                            remaining_product_number = purchase.product.amount,
                            action = "Anbardan silindi"
                        )

                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = purchase.supplier,
                            product = purchase.product,
                            date = purchase.date,
                            product_price = purchase.price * purchase.amount,
                            action = "Məhsul alışı ləğv edildi"
                        )

                    elif purchase.status == 'G' and p_status == 'A':
                        purchase.status = 'A'
                        purchase.save()
                        stock, created = Stock.objects.get_or_create(
                            product = purchase.product
                        )
                        stock.amount = stock.amount + purchase.amount
                        stock.save()
                        purchase.product.amount = stock.amount
                        purchase.product.save()

                        ProductAction.objects.create(
                            product = purchase.product,
                            date = purchase.date,
                            incoming_product_number = purchase.amount,
                            remaining_product_number = purchase.product.amount,
                            action = "Anbara əlavə edildi"
                        )

                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = purchase.supplier,
                            product = purchase.product,
                            date = purchase.date,
                            product_price = purchase.price * purchase.amount,
                            action = "Məhsul alışı icra edildi"
                        )
            if date:
                purchases.update(date=date)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PurchaseListDestroyAPIView(DestroyAPIView):
    queryset = PurchaseList.objects.all()
    serializer_class = PurchaseListDestroySerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        purchases = instance.purchaselist_purchases.filter(status='A')
        customeractionlist = CustomerActionList.objects.create()

        for purchase in purchases:
            if hasattr(purchase.product, "stock"):
                purchase.product.stock.amount = purchase.product.stock.amount - purchase.amount
                if purchase.product.stock.amount > 0:
                    purchase.product.stock.save()
                    purchase.product.amount = purchase.product.stock.amount
                    purchase.product.save()

                    ProductAction.objects.create(
                        product = purchase.product,
                        date = timezone.now(),
                        remaining_product_number = purchase.product.stock.amount,
                        action = "Anbardan silindi"
                    )
                    CustomerAction.objects.create(
                        customeractionlist = customeractionlist,
                        customer = purchase.supplier,
                        product = purchase.product,
                        date = timezone.now(),
                        product_price = purchase.price * purchase.amount,
                        action = "Məhsul alışı ləğv edildi"
                    )

                else:
                    purchase.product.stock.delete()
                    purchase.product.amount = 0
                    purchase.product.save()

                    ProductAction.objects.create(
                        product = purchase.product,
                        date = timezone.now(),
                        remaining_product_number = 0,
                        action = "Anbardan silindi"
                    )
                    CustomerAction.objects.create(
                        customeractionlist = customeractionlist,
                        customer = purchase.supplier,
                        product = purchase.product,
                        date = timezone.now(),
                        product_price = purchase.price * purchase.amount,
                        action = "Məhsul alışı ləğv edildi"
                    )

        return super().delete(request, *args, **kwargs)

class BulkPurchaseAPIView(APIView):
    def post(self, request):
        serializer = BulkPurchaseSerializer(data=request.data)
        if serializer.is_valid():
            purchaselist_id = serializer.validated_data.get("purchaselist")
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

            supplier = get_object_or_404(CustomUser, id=supplier_id)
            customeractionlist = CustomerActionList.objects.create()

            if purchaselist_id:
                purchaselist = PurchaseList.objects.get(id=purchaselist_id)
                for i in range(len(products)):
                    product = get_object_or_404(Product, id=products[i])
                    purchase, created = Purchase.objects.get_or_create(
                        supplier = supplier,
                        product = product,
                        purchaselist = purchaselist
                        # amount = amounts[i],
                        # date = date,
                        # status = p_status,
                    )
                    if created:
                        purchase.amount = amounts[i]
                        purchase.date = date
                        purchase.status = p_status
                        purchase.price = purchase_prices[i]
                        purchase.save()
                        product.purchase_price = purchase_prices[i]
                        product.cost_price = cost_prices[i]
                        product.price = prices[i]
                        product.discount_price = discount_prices[i]
                        product.currency = currency
                        # product.amount = product.amount + amounts[i]
                        product.updated_at_purchase_time = timezone.now()
                        product.save()

                        if p_status == "A":
                            stock, created = Stock.objects.get_or_create(
                                product = product
                            )
                            stock.amount = stock.amount + amounts[i]
                            stock.save()
                            product.amount = stock.amount
                            product.save()

                            ProductAction.objects.create(
                                product = product,
                                date = date,
                                incoming_product_number = amounts[i],
                                remaining_product_number = stock.amount,
                                action = "Anbara əlavə edildi"
                            )
                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = supplier,
                                product = product,
                                date = date,
                                product_price = purchase_prices[i] * amounts[i],
                                action = "Məhsul alışı icra edildi"
                            )
                        else:
                            if customeractionlist.id is not None:
                                customeractionlist.delete()
                    else:
                        old_p_amount = purchase.amount
                        purchase.amount = amounts[i]
                        purchase.date = date
                        purchase.status = p_status
                        purchase.price = purchase_prices[i]
                        purchase.save()
                        product.purchase_price = purchase_prices[i]
                        product.cost_price = cost_prices[i]
                        product.price = prices[i]
                        product.discount_price = discount_prices[i]
                        product.currency = currency
                        # product.amount = product.amount + amounts[i]
                        product.updated_at_purchase_time = timezone.now()
                        product.save()

                        if p_status == "A":
                            stock, created = Stock.objects.get_or_create(
                                product = product
                            )
                            stock.amount = stock.amount - old_p_amount + amounts[i]
                            stock.save()
                            product.amount = stock.amount
                            product.save()

                            ProductAction.objects.create(
                                product = product,
                                date = date,
                                incoming_product_number = amounts[i] - old_p_amount,
                                remaining_product_number = stock.amount,
                                action = "Anbara əlavə edildi"
                            )

                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = supplier,
                                product = product,
                                date = date,
                                product_price = purchase_prices[i] * (amounts[i] - old_p_amount),
                                action = "Məhsul alışı icra edildi"
                            )
                        else:
                            if customeractionlist.id is not None:
                                customeractionlist.delete()

            else:
                purchaselist = PurchaseList.objects.create(currency=currency)
                for i in range(len(products)):
                    product = get_object_or_404(Product, id=products[i])
                    Purchase.objects.create(
                        supplier = supplier,
                        product = product,
                        purchaselist = purchaselist,
                        amount = amounts[i],
                        price = purchase_prices[i],
                        date = date,
                        status = p_status,
                    )
                    product.purchase_price = purchase_prices[i]
                    product.cost_price = cost_prices[i]
                    product.price = prices[i]
                    product.discount_price = discount_prices[i]
                    product.currency = currency
                    # product.amount = product.amount + amounts[i]
                    product.updated_at_purchase_time = timezone.now()
                    product.save()

                    if p_status == "A":
                        stock, created = Stock.objects.get_or_create(
                            product = product
                        )
                        stock.amount = stock.amount + amounts[i]
                        stock.save()
                        product.amount = stock.amount
                        product.save()

                        ProductAction.objects.create(
                            product = product,
                            date = date,
                            incoming_product_number = amounts[i],
                            remaining_product_number = stock.amount,
                            action = "Anbara əlavə edildi"
                        )

                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = supplier,
                            product = product,
                            date = date,
                            product_price = purchase_prices[i] * amounts[i],
                            action = "Məhsul alışı icra edildi"
                        )
                    else:
                        if customeractionlist.id is not None:
                            customeractionlist.delete()

            response_data = {
                "message": f"{len(products)} məhsul alışı icra edildi."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockListAPIView(ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["product__name", "product__articles__name", "product__brand__name"]

class AddToStockAPIView(APIView):
    def post(self, request):
        serializer = AddToStockSerializer(data=request.data)

        if serializer.is_valid():
            item_ids = serializer.validated_data["item_ids"]
            items = Purchase.objects.filter(id__in=item_ids)
            
            customeractionlist = CustomerActionList.objects.create()

            for item in items:
                stock, created = Stock.objects.get_or_create(
                    product = item.product
                )
                stock.amount = stock.amount + item.amount
                stock.save()
                item.status = "A"
                item.save()
                item.product.amount = stock.amount
                item.product.save()

                ProductAction.objects.create(
                    product = item.product,
                    date = item.date,
                    incoming_product_number = item.amount,
                    remaining_product_number = stock.amount,
                    action = "Anbara əlavə edildi"
                )

                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = item.supplier,
                    product = item.product,
                    date = item.date,
                    product_price = item.price * item.amount,
                    action = "Məhsul alışı icra edildi"
                )
                
            response_data = {
                "message": f"{len(items)} məhsul anbara əlavə edildi."
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StockRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockUpdateSerializer
    lookup_field = "id"

# class ShortSaleListAPIView(ListAPIView):
#     queryset = Sale.objects.all()
#     serializer_class = ShortSaleSerializer
#     pagination_class = CustomPagination
#     filter_backends = [filters.SearchFilter]
#     search_fields = ["customer__username", "customer__first_name", "customer__last_name", "product__name", "product__store__name"]

from django.db.models import Value, CharField, Case, When, F
from django.db.models.functions import Concat

class ShortSaleListAPIView(ListAPIView):
    serializer_class = ShortSaleSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]

    search_fields = ["sale_text"]   # <- annotate olunan field

    def get_queryset(self):
        full_name = Concat(
            F("customer__first_name"), Value(" "), F("customer__last_name")
        )

        customer_name = Case(
            When(
                customer__first_name__isnull=False,
                customer__first_name__gt="",
                customer__last_name__isnull=False,
                customer__last_name__gt="",
                then=full_name
            ),
            default=F("customer__username"),
            output_field=CharField()
        )

        return (
            Sale.objects
            .select_related("customer", "product", "product__store")
            .annotate(
                sale_text=Concat(
                    customer_name,
                    Value(" - "),
                    F("product__name"),
                    Value(" - "),
                    F("product__store__name"),
                    Value(" ("),
                    F("datetime"),
                    Value(")"),
                    output_field=CharField()

                )
            )
        )

class SaleListAPIView(ListAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class SaleListListAPIView(ListAPIView):
    def get_queryset(self):
        return SaleList.objects.annotate(
                dt=Max("salelist_sales__datetime")
            ).order_by("-dt")
    serializer_class = SaleListSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, TotalDebtFilterBackend, SaleDateFilterBackend]
    search_fields = ["salelist_sales__seller__username", "salelist_sales__seller__first_name", "salelist_sales__seller__last_name", "salelist_sales__customer__username", "salelist_sales__customer__first_name", "salelist_sales__customer__last_name", "salelist_sales__status"]

class SaleListRetrieveAPIView(RetrieveAPIView):
    queryset = SaleList.objects.all()
    serializer_class = SaleListRetrieveSerializer
    lookup_field = "id"

class SaleListUpdateAPIView(UpdateAPIView):
    queryset = SaleList.objects.all()
    serializer_class = SaleListUpdateSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)

        if serializer.is_valid():
            customer_id = serializer.validated_data.get("customer_id")
            s_status = serializer.validated_data.get("status")
            dt = serializer.validated_data.get("dt")
            customeractionlist = CustomerActionList.objects.create()

            sales = instance.salelist_sales.all()
            if customer_id:
                customer = get_object_or_404(CustomUser, id=customer_id)
                for sale in sales:
                    sale.customer = customer
                    sale.save()
            if s_status:
                for sale in sales:
                    if sale.status == "S" and s_status == "G":
                        sale.status = "G"
                        sale.save()
                        stock, created = Stock.objects.get_or_create(
                            product = sale.product
                        )
                        stock.amount = stock.amount + sale.amount
                        stock.save()
                        sale.product.amount = stock.amount

                        # if customeractionlist.id is None:
                        #     customeractionlist.delete()

                        ProductAction.objects.create(
                            product = sale.product,
                            customer = sale.customer,
                            date = dt,
                            remaining_product_number = sale.product.amount,
                            action = "Anbara əlavə edildi"
                        )
                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = sale.customer,
                            product = sale.product,
                            date = dt,
                            product_price = sale.price * sale.amount,
                            action = "Məhsul satışı ləğv edildi"
                        )
                    elif sale.status == "G" and s_status == "S":
                        stock, created = Stock.objects.get_or_create(
                            product = sale.product
                        )
                        if stock.amount >= sale.amount: 
                            stock.amount = stock.amount - sale.amount
                            stock.save()
                            sale.status = "S"
                            sale.save()
                            sale.product.amount = stock.amount
                        else:
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        
                        ProductAction.objects.create(
                            product = sale.product,
                            customer = sale.customer,
                            date = dt,
                            sold_product_number = sale.amount,
                            remaining_product_number = sale.product.amount,
                            action = "Məhsul satıldı"
                        )
                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = sale.customer,
                            product = sale.product,
                            date = dt,
                            product_price = sale.price * sale.amount,
                            action = "Məhsul satışı icra edildi"
                        )
                    sale.product.save()
            if dt:
                sales.update(datetime=dt)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
    
class SaleListDestroyAPIView(DestroyAPIView):
    queryset = SaleList.objects.all()
    serializer_class = SaleListDestroySerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        sales = instance.salelist_sales.filter(status='S')
        customeractionlist = CustomerActionList.objects.create()

        for sale in sales:
            if hasattr(sale.product, "stock"):
                sale.product.stock.amount = sale.product.stock.amount + sale.amount
                sale.product.stock.save()
                sale.product.amount = sale.product.stock.amount
                sale.product.save()

                ProductAction.objects.create(
                    product = sale.product,
                    date = timezone.now(),
                    remaining_product_number = sale.product.stock.amount,
                    action = "Anbara əlavə edildi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = sale.customer,
                    product = sale.product,
                    date = timezone.now(),
                    product_price = sale.price * sale.amount,
                    action = "Məhsul satışı ləğv edildi"
                )

        return super().delete(request, *args, **kwargs)

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
            # product.amount = product.amount - int(sale_data["amount"])
            # product.save()
            if hasattr(product, "stock"):
                product.stock.amount = product.stock.amount - int(sale_data["amount"])
                product.stock.save()
                product.amount = product.stock.amount
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
                product_price = int(sale_data["price"]) * int(sale_data["amount"])
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

            customeractionlist = CustomerActionList.objects.create()

            if previous_instance_status == "G" and instance.status == "S":
                instance.product.amount = instance.product.amount - instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount - instance.amount
                    instance.product.stock.save()
                ProductAction.objects.create(
                    product = instance.product,
                    customer = instance.customer,
                    date = instance.datetime.date(), 
                    sold_product_number = instance.amount,
                    remaining_product_number = instance.product.amount,
                    action = "Məhsul satıldı"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.customer,
                    product = instance.product,
                    date = instance.datetime.date(), 
                    product_price = instance.price * instance.amount,
                    action = "Məhsul satışı icra edildi"
                )
            elif previous_instance_status == "S" and instance.status == "G":
                instance.product.amount = instance.product.amount + instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount + instance.amount
                    instance.product.stock.save()
                ProductAction.objects.create(
                    product = instance.product,
                    customer = instance.customer,
                    date = instance.datetime.date(), 
                    remaining_product_number = instance.product.amount,
                    action = "Anbara əlavə edildi"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.customer,
                    product = instance.product,
                    date = instance.datetime.date(), 
                    product_price = instance.price * instance.amount,
                    action = "Məhsul satışı ləğv edildi"
                )
            elif previous_instance_status == "S" and instance.status == "S":
                instance.product.amount = instance.product.amount + previous_instance_amount - instance.amount
                instance.product.save()
                if hasattr(instance.product, "stock"):
                    instance.product.stock.amount = instance.product.stock.amount + previous_instance_amount - instance.amount
                    instance.product.stock.save()
                ProductAction.objects.create(
                    product = instance.product,
                    customer = instance.customer,
                    date = instance.datetime.date(), 
                    sold_product_number = instance.amount - previous_instance_amount,
                    remaining_product_number = instance.product.amount,
                    action = "Məhsul satıldı"
                )
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = instance.customer,
                    product = instance.product,
                    date = instance.datetime.date(), 
                    product_price = instance.price * instance.amount,
                    action = "Məhsul satışı icra edildi"
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'S':
            instance.product.stock.amount = instance.product.stock.amount + instance.amount
            customeractionlist = CustomerActionList.objects.create()
            instance.product.stock.save()
            instance.product.amount = instance.product.stock.amount
            instance.product.save()
            ProductAction.objects.create(
                product = instance.product,
                date = instance.datetime.date(),
                remaining_product_number = instance.product.stock.amount,
                action = "Anbara əlavə edildi"
            )
            CustomerAction.objects.create(
                customeractionlist = customeractionlist,
                customer = instance.customer,
                product = instance.product,
                date = instance.datetime.date(),
                product_price = instance.price * instance.amount,
                action = "Məhsul satışı ləğv edildi"
            )
            
        return super().delete(request, *args, **kwargs)

    
class BulkSaleAPIView(APIView):
    def post(self, request):
        serializer = BulkSaleSerializer(data=request.data)
        if serializer.is_valid():
            salelist_id = serializer.validated_data.get("salelist")
            customer_id = serializer.validated_data["customer"]
            products_id = serializer.validated_data["products"]
            prices = serializer.validated_data["prices"]
            amounts = serializer.validated_data["amounts"]
            datetimes = serializer.validated_data["datetimes"]
            statuses = serializer.validated_data["statuses"]

            seller = request.user
            customer = CustomUser.objects.get(id=customer_id)
            customeractionlist = CustomerActionList.objects.create()

            if salelist_id:
                salelist = SaleList.objects.get(id=salelist_id)
                for i in range(len(products_id)):
                    product = get_object_or_404(Product, id=products_id[i])
                    sale, created = Sale.objects.get_or_create(
                        customer = customer,
                        salelist = salelist,
                        product = product, 
                        # datetime = datetimes[i],
                        # price = prices[i],
                    )
                    if created:
                        sale.seller = request.user
                        sale.status = statuses[i]
                        sale.amount = amounts[i]
                        sale.datetime = datetimes[i]
                        sale.price = prices[i]
                        sale.save()
                        if sale.status == "S":
                            product.amount = product.amount - sale.amount
                            product.save()
                            if hasattr(product, "stock"):
                                product.stock.amount = product.stock.amount - sale.amount
                                product.stock.save()
                            
                            ProductAction.objects.create(
                                product = product,
                                customer = customer,
                                date = datetimes[i].date(), 
                                sold_product_number = amounts[i],
                                remaining_product_number = product.amount,
                                action = "Məhsul satıldı"
                            )
                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = customer,
                                product = product,
                                date = datetimes[i].date(), 
                                product_price = prices[i] * amounts[i],
                                action = "Məhsul satışı icra edildi"
                            )
                        else:
                            if customeractionlist.id is not None:
                                customeractionlist.delete()
                    else:
                        old_sale_status = sale.status
                        old_sale_amount = sale.amount
                        sale.amount = amounts[i]
                        sale.status = statuses[i]
                        sale.datetime = datetimes[i]
                        sale.price = prices[i]
                        sale.save()
                        if old_sale_status == "S" and sale.status == "G":
                            product.amount = product.amount + old_sale_amount
                            product.save()
                            if hasattr(product, "stock"):
                                product.stock.amount = product.amount
                                product.stock.save()

                            if customeractionlist.id is not None:
                                customeractionlist.delete()

                            ProductAction.objects.create(
                                product = product,
                                customer = customer,
                                date = datetimes[i].date(),
                                remaining_product_number = product.amount,
                                action = "Anbara əlavə edildi"
                            )
                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = customer,
                                product = product,
                                date = datetimes[i].date(), 
                                product_price = prices[i] * amounts[i],
                                action = "Məhsul satışı ləğv edildi"
                            )

                        elif old_sale_status == "G" and sale.status == "S":
                            product.amount = product.amount - sale.amount
                            product.save()
                            if hasattr(product, "stock"):
                                product.stock.amount = product.amount
                                product.stock.save()

                            ProductAction.objects.create(
                                product = product,
                                customer = customer,
                                date = datetimes[i].date(), 
                                sold_product_number = amounts[i],
                                remaining_product_number = product.amount,
                                action = "Məhsul satıldı"
                            )
                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = customer,
                                product = product,
                                date = datetimes[i].date(), 
                                product_price = prices[i] * amounts[i],
                                action = "Məhsul satışı icra edildi"
                            )
                        elif old_sale_status == "S" and sale.status == "S":
                            product.amount = product.amount + old_sale_amount - sale.amount
                            product.save()
                            if hasattr(product, "stock"):
                                product.stock.amount = product.amount
                                product.stock.save()

                            ProductAction.objects.create(
                                product = product,
                                customer = customer,
                                date = datetimes[i].date(), 
                                sold_product_number = amounts[i] - old_sale_amount,
                                remaining_product_number = product.amount,
                                action = "Məhsul satıldı"
                            )
                            CustomerAction.objects.create(
                                customeractionlist = customeractionlist,
                                customer = customer,
                                product = product,
                                date = datetimes[i].date(), 
                                product_price = prices[i] * (amounts[i] - old_sale_amount),
                                action = "Məhsul satışı icra edildi"
                            )
                    
                    print("Saved value:", sale.datetime, sale.datetime.tzinfo)
            else:
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
                            remaining_product_number = product.amount,
                            action = "Məhsul satıldı"
                        )
                        CustomerAction.objects.create(
                            customeractionlist = customeractionlist,
                            customer = customer,
                            product = product,
                            date = datetimes[i].date(), 
                            product_price = prices[i] * amounts[i],
                            action = "Məhsul satışı icra edildi"
                        )
                    else:
                        if customeractionlist.id is not None:
                            customeractionlist.delete()

            
            response_data = {
                "message": f"Seçilmiş məhsullar '{customer}' müştəriyə satıldı."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["customer__username", "customer__first_name", "customer__last_name"]

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
            # customer_debt = sum([sale.price * sale.amount for sale in customer.customer_sales.all()])
            previous_input_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassaya giriş")]
            previous_output_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassa girişi ləğv edildi")]
            previous_total_amount = 0 if not previous_input_amounts else sum(previous_input_amounts, start=0) - sum(previous_output_amounts, 0)
            c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
            c_sales = Sale.objects.filter(customer=customer, status="S")
            c_payments = Payment.objects.filter(customer=customer)
            c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

            total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
            total_c_payments = sum(payment.amount for payment in c_payments)
            total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
            total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

            total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments
            dt = payment_data["datetime"].split("T")[0]
            dt_data = dt.split("-")

            customeractionlist = CustomerActionList.objects.create()

            CustomerAction.objects.create(
                customeractionlist = customeractionlist,
                customer = customer,
                date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                payment_amount = payment_data["amount"],
                total_amount = previous_total_amount + float(payment_data["amount"]),
                remaining_amount = total_c_debt,
                action = "Kassaya giriş"
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            old_customer = instance.customer
            old_amount = instance.amount
            serializer.save()
            customer = serializer.validated_data.get("customer")
            amount = serializer.validated_data.get("amount")

            dt = serializer.validated_data["datetime"].date()

            previous_input_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassaya giriş")]
            previous_output_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassa girişi ləğv edildi")]
            previous_total_amount = 0 if not previous_input_amounts else sum(previous_input_amounts, start=0) - sum(previous_output_amounts, 0)
            c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
            c_sales = Sale.objects.filter(customer=customer, status="S")
            c_payments = Payment.objects.filter(customer=customer)
            c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

            total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
            total_c_payments = sum(payment.amount for payment in c_payments)
            total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
            total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

            total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments

            if customer != old_customer:
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = old_customer,
                    date = dt,
                    payment_amount = old_amount,
                    total_amount = previous_total_amount + float(amount),
                    remaining_amount = total_c_debt,
                    action = "Kassa girişi ləğv edildi"
                )
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = customer,
                    date = dt,
                    payment_amount = amount,
                    total_amount = previous_total_amount + float(amount),
                    remaining_amount = total_c_debt,
                    action = "Kassaya giriş"
                )
            else:
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = customer,
                    date = dt,
                    payment_amount = amount - old_amount,
                    total_amount = previous_total_amount + float(amount-old_amount),
                    remaining_amount = total_c_debt,
                    action = "Kassaya giriş"
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        customeractionlist = CustomerActionList.objects.create()

        customer = instance.customer

        previous_input_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassaya giriş")]
        previous_output_amounts = [action.payment_amount if action.payment_amount else 0 for action in customer.customer_actions.filter(action="Kassa girişi ləğv edildi")]
        previous_total_amount = 0 if not previous_input_amounts else sum(previous_input_amounts, start=0) - sum(previous_output_amounts, 0)
        c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
        c_sales = Sale.objects.filter(customer=customer, status="S")
        c_payments = Payment.objects.filter(customer=customer)
        c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

        total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
        total_c_payments = sum(payment.amount for payment in c_payments)
        total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
        total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

        total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments
        
        CustomerAction.objects.create(
            customeractionlist = customeractionlist,
            customer = customer,
            date = timezone.now(),
            payment_amount = instance.amount,
            total_amount = previous_total_amount - float(instance.amount),
            remaining_amount = total_c_debt + instance.amount,
            action = "Kassa girişi ləğv edildi"
        )
        return super().delete(request, *args, **kwargs)

                

class ProductActionListAPIView(ListAPIView):

    def get_queryset(self):
        product_id = self.kwargs.get("id")
        product = get_object_or_404(Product, id=product_id)
        return ProductAction.objects.filter(
            product = product
        )
    serializer_class = ProductActionSerializer

class CustomerActionListAPIView(APIView):
    def get(self, request, id):
        customer_id = self.kwargs.get("id")
        customer = get_object_or_404(CustomUser, id=customer_id)
        customeractionlists = CustomerActionList.objects.filter(
            c_customer_actions__in=customer.customer_actions.all()
        ).distinct()
        # customeractions = CustomerAction.objects.filter(
        #     customer = customer,
        #     customeractionlist = None
        # )

        cl_data = CustomerActionListSerializer(customeractionlists, many=True).data
        # c_data = CustomerActionSerializer(customeractions, many=True).data

        response_data = cl_data

        return Response(response_data, status=status.HTTP_200_OK)
    
class CustomerActionListRetrieveAPIView(ListAPIView):
    def get_queryset(self):
        customeractionlist_id = self.kwargs.get("id")
        customeractionlist = CustomerActionList.objects.get(id=customeractionlist_id)
        return CustomerAction.objects.filter(customeractionlist=customeractionlist)
    serializer_class = CustomerActionSerializer

class ReturnBackListAPIView(ListAPIView):
    queryset = ReturnBack.objects.all()
    serializer_class = ReturnBackSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["sale__customer__username", "sale__customer__first_name", "sale__customer__last_name", "sale__product__name", "sale__product__articles__name", "reason"]

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
                return_product_number = float(amount),
                remaining_product_number = sale.product.amount,
                action = "Geri qaytarıldı"
            )
            customeractionlist = CustomerActionList.objects.create()
            CustomerAction.objects.create(
                customeractionlist = customeractionlist,
                customer = sale.customer,
                product = sale.product,
                date = request.data.get("date"),
                product_price = sale.price * sale.amount,
                return_amount = sale.price * float(amount),
                action = "Geri qaytarma icra olundu"
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

            ProductAction.objects.create(
                product = instance.sale.product,
                customer = instance.sale.customer,
                date = request.data.get("date"),
                return_product_number = instance.amount - previous_instance_amount,
                remaining_product_number = instance.sale.product.amount,
                action = "Geri qaytarıldı"
            )
            customeractionlist = CustomerActionList.objects.create()
            CustomerAction.objects.create(
                customeractionlist = customeractionlist,
                customer = instance.sale.customer,
                product = instance.sale.product,
                date = request.data.get("date"),
                product_price = instance.sale.price * instance.amount,
                return_amount = instance.sale.price * instance.amount,
                action = "Geri qaytarma icra olundu"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.sale.amount = instance.sale.amount + instance.amount
        instance.sale.save()
        instance.sale.product.amount = instance.sale.product.amount - instance.amount
        instance.sale.product.save()

        if hasattr(instance.sale.product, "stock"):
            instance.sale.product.stock.amount = instance.sale.product.stock.amount - instance.amount
            instance.sale.product.stock.save()

        ProductAction.objects.create(
            product = instance.sale.product,
            customer = instance.sale.customer,
            date = timezone.now().date(),
            return_product_number = instance.amount,
            remaining_product_number = instance.sale.product.amount,
            action = "Geri qaytarma ləğv edildi"
        )
        customeractionlist = CustomerActionList.objects.create()
        CustomerAction.objects.create(
            customeractionlist = customeractionlist,
            customer = instance.sale.customer,
            product = instance.sale.product,
            date = timezone.now().date(),
            product_price = instance.sale.price * instance.amount,
            return_amount = instance.sale.price * instance.amount,
            action = "Geri qaytarma ləğv edildi"
        )
        return super().delete(request, *args, **kwargs)


class ExpenseListAPIView(ListAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

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
            purchases = Purchase.objects.filter(
                date__month = m, date__year = year
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
            purchases = Purchase.objects.filter(
                date__year = year
            )
        if user.is_superuser:
            total_income = sum([payment.amount for payment in payments])
            total_outcome = sum([expense.amount for expense in expenses])
            total_returnback = sum([returnback.amount * returnback.sale.price for returnback in returnbacks])
            total_m_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="M")])
            total_d_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="D")])
            total_r_supplierpayments = sum([payment.amount for payment in supplierpayments.filter(currency="R")])
            total_m_purchase = sum([purchase.price * purchase.amount for purchase in purchases.filter(status="A", purchaselist__currency="M")])
            total_d_purchase = sum([purchase.price * purchase.amount for purchase in purchases.filter(status="A", purchaselist__currency="D")])
            total_r_purchase = sum([purchase.price * purchase.amount for purchase in purchases.filter(status="A", purchaselist__currency="R")])
            total_stock_value = sum([stock.product.cost_price * stock.amount for stock in Stock.objects.all()])
        else:
            sales = sales.filter(seller=user)
            total_income = None
            total_outcome = None
            total_returnback = None
            total_m_supplierpayments = None
            total_d_supplierpayments = None
            total_r_supplierpayments = None
            total_m_purchase = None
            total_d_purchase = None
            total_r_purchase = None
            total_stock_value = None
        sold_product_number = sum([sale.amount for sale in sales])
        customer_number = sales.values('customer').distinct().count()
        total_sale_amount = sum([sale.price * sale.amount for sale in sales])
        total_cost_amount = sum([Decimal(str(sale.product.cost_price)) * Decimal(str(sale.amount)) for sale in sales])
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
            "total_supplier_r_payment_amount": total_r_supplierpayments,
            "total_m_purchase": total_m_purchase,
            "total_d_purchase": total_d_purchase,
            "total_r_purchase": total_r_purchase,
            "total_stock_value": total_stock_value
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
            elif user.is_staff:
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
            else:
                for i in range(len(months)):
                    year = datetime.datetime.now().year
                    # if brand_id:
                    #     sales = Sale.objects.filter(
                    #         seller = user,
                    #         product__brand__id = brand_id,
                    #         datetime__date__month = i + 1,
                    #         datetime__date__year = year,
                    #         status = "S"
                    #     )
                    sales = Sale.objects.filter(
                        customer = user,
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
        
# class MostInDebtedCustomerAPIView(APIView):
#     def get(self, request):
#         customers = CustomUser.objects.all()
#         customer_debts = []
#         for customer in customers:
#             customer_debt = sum([sale.price * sale.amount for sale in customer.customer_sales.all()]) - sum([payment.amount for payment in customer.payments.all()])
#             customer_debts.append(customer_debt)
        
#         indebted_customers = list(zip(customers, customer_debts))
#         indebted_customers.sort(reverse=True, key=lambda x: x[1])
#         most_indebted_customers = indebted_customers[:5]
#         customers_data = []
#         for customer in most_indebted_customers:
#             customer_data = {
#                 "name": customer[0].username,
#                 "debt": customer[1],
#                 "phone_number": customer[0].phone_number
#             }
#             customers_data.append(customer_data)
#         response_data = {"most_indebted_customers": customers_data}
#         return Response(response_data, status=status.HTTP_200_OK)

from django.db.models import Sum, F, Q, Value, FloatField, Subquery, OuterRef, Prefetch
from django.db.models.functions import Coalesce

class MostInDebtedCustomerAPIView(APIView):
    def get(self, request):
        # Annotate ilə borc hesablayırıq
        # customers = (
        #     CustomUser.objects
        #     .annotate(
        #         total_sales=Coalesce(Sum(F("customer_sales__price") * F("customer_sales__amount"), filter=Q(customer_sales__status="S"), output_field=FloatField()), Value(0.0)),
        #         total_payments=Coalesce(Sum("payments__amount", output_field=FloatField()), Value(0.0))
        #     )
        #     .annotate(debt=F("total_sales") - F("total_payments"))
        #     .filter(debt__gt=0)
        #     .order_by("-debt")
        # )
        
        # # Pagination tətbiq edirik
        # paginator = CustomPagination()
        # paginated_customers = paginator.paginate_queryset(customers, request)

        # # Data serialize edirik
        # customers_data = [
        #     {
        #         "name": customer.username,
        #         "debt": customer.debt if customer.debt else 0,
        #         "phone_number": customer.phone_number,
        #     }
        #     for customer in paginated_customers
        # ]

        # return paginator.get_paginated_response(customers_data)


        customers = CustomUser.objects.prefetch_related(
            "customer_sales",
            "payments"
        )

        # Python səviyyəsində borc hesablayırıq
        customers_with_debt = []
        for customer in customers:
            # Statusu "S" olan satışları götürürük
            total_sales = sum(
                s.price * s.amount for s in customer.customer_sales.all() if s.status == "S"
            )
            total_m_purchases = sum(
                p.price * p.amount for p in customer.supplier_purchases.all() if p.status == "A" and p.purchaselist.currency == "M"
            )
            total_payments = sum(p.amount for p in customer.payments.all())
            total_supplier_payments = sum(p.amount for p in customer.supplier_payments.filter(currency = "M"))
            debt = total_sales - total_payments - total_m_purchases + total_supplier_payments

            if debt > 0:
                customers_with_debt.append({
                    "name": customer.username,
                    "debt": float(debt),
                    "phone_number": customer.phone_number,
                })

        # Borca görə azalan sıraya düzürük
        customers_with_debt.sort(key=lambda x: x["debt"], reverse=True)

        # Pagination tətbiq edirik
        paginator = CustomPagination()
        paginated_customers = paginator.paginate_queryset(customers_with_debt, request)

        return paginator.get_paginated_response(paginated_customers)
    
class StockOutProductsListAPIView(ListAPIView):
    def get_queryset(self):
        return Product.objects.filter(amount__lte=20)
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "articles__name", "brand__name", "store__name", "category__name"]

class SupplierPaymentListAPIView(ListAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["supplier__username", "supplier__first_name", "supplier__last_name"]

class SupplierPaymentCreateAPIView(CreateAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentCreateSerializer

    def create(self, request, *args, **kwargs):
        payment_data = {
            "supplier": request.data.get("supplier"),
            "currency": request.data.get("currency"),
            "datetime": request.data.get("datetime"),
            "amount": request.data.get("amount")
        }
        serializer = self.get_serializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            customer = CustomUser.objects.get(id=payment_data["supplier"])
            # customer_debt = sum([sale.price * sale.amount for sale in customer.customer_sales.all()])
            c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
            c_sales = Sale.objects.filter(customer=customer, status="S")
            c_payments = Payment.objects.filter(customer=customer)
            c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

            total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
            total_c_payments = sum(payment.amount for payment in c_payments)
            total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
            total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

            total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments
            dt = payment_data["datetime"].split("T")[0]
            dt_data = dt.split("-")

            customeractionlist = CustomerActionList.objects.create()

            CustomerAction.objects.create(
                customeractionlist = customeractionlist,
                customer = customer,
                date = datetime.date(year=int(dt_data[0]), month=int(dt_data[1]), day=int(int(dt_data[2]))),
                payment_amount = payment_data["amount"],
                total_amount = 0,
                remaining_amount = total_c_debt,
                action = "Kassadan çıxış"
            )

            response_data = {
                "message": "Ödəniş əlavə olundu."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SupplierPaymentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SupplierPayment.objects.all()
    serializer_class = SupplierPaymentCreateSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            old_customer = instance.supplier
            old_amount = instance.amount
            serializer.save()
            customer = serializer.validated_data.get("supplier")
            amount = serializer.validated_data.get("amount")

            dt = serializer.validated_data["datetime"].date()

            c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
            c_sales = Sale.objects.filter(customer=customer, status="S")
            c_payments = Payment.objects.filter(customer=customer)
            c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

            total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
            total_c_payments = sum(payment.amount for payment in c_payments)
            total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
            total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

            total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments

            if customer != old_customer:
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = old_customer,
                    date = dt,
                    payment_amount = old_amount,
                    total_amount = 0,
                    remaining_amount = total_c_debt,
                    action = "Kassa çıxışı ləğv edildi"
                )
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = customer,
                    date = dt,
                    payment_amount = amount,
                    total_amount = 0,
                    remaining_amount = total_c_debt,
                    action = "Kassadan çıxış"
                )
            else:
                customeractionlist = CustomerActionList.objects.create()
                CustomerAction.objects.create(
                    customeractionlist = customeractionlist,
                    customer = customer,
                    date = dt,
                    payment_amount = amount - old_amount,
                    total_amount = 0,
                    remaining_amount = total_c_debt,
                    action = "Kassadan çıxış"
                )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        customeractionlist = CustomerActionList.objects.create()

        customer = instance.supplier

        c_purchases = Purchase.objects.filter(supplier=customer, status="A", purchaselist__currency="M")
        c_sales = Sale.objects.filter(customer=customer, status="S")
        c_payments = Payment.objects.filter(customer=customer)
        c_supplierpayments = SupplierPayment.objects.filter(supplier=customer)

        total_c_sale = sum(sale.price * sale.amount for sale in c_sales)
        total_c_payments = sum(payment.amount for payment in c_payments)
        total_c_purchases = sum(purchase.price * purchase.amount for purchase in c_purchases)
        total_c_supplierpayments = sum(supplierpayment.amount for supplierpayment in c_supplierpayments)

        total_c_debt = total_c_sale - total_c_payments - total_c_purchases + total_c_supplierpayments


        
        CustomerAction.objects.create(
            customeractionlist = customeractionlist,
            customer = customer,
            date = timezone.now(),
            payment_amount = instance.amount,
            total_amount = 0,
            remaining_amount = total_c_debt + instance.amount,
            action = "Kassadan çıxış ləğv edildi"
        )
        return super().delete(request, *args, **kwargs)