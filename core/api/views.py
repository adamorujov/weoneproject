from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Store, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem
)
from core.api.serializers import (
    CustomUserCreateSerializer, CustomUserSerializer, CustomUserSerializer, SiteSettingsSerializer, BannerSerializer, ProductCategorySerializer, ProductCreateSerializer,
    ProductUpdateSerializer, ArticleSerializer, BrandSerializer, StoreSerializer, ProductSerializer, ApplicationSerializer, SocialMediaSerializer, AdvantageSerializer,
    ActivitySerializer, ServiceSerializer, MissionSerializer, BasketItemSerializer, BasketItemCreateSerializer, BasketCleanSerializer,
    OrderCreateSerializer
)
from django.shortcuts import get_object_or_404
import json

class UserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (IsAdminUser,)

class UserListAPIView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminUser,)

class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = "id"

class SupplierListAPIView(ListAPIView):
    def get_queryset(self):
        return CustomUser.objects.filter(is_supplier=True)
    serializer_class = CustomUserSerializer

class SiteSettingsListAPIView(ListAPIView):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer
    
class BannerListAPIView(ListAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

class ProductCategoryListAPIView(ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class BrandListAPIView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class StoreListAPIView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CategoryProductListAPIView(ListAPIView):
    def get_queryset(self):
        category_id = self.kwargs.get("id")
        category = ProductCategory.objects.get(id=category_id)
        return Product.objects.filter(
            category = category
        )
    serializer_class = ProductSerializer

class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer

    def create(self, request, *args, **kwargs):
        product_data = {
            "name": request.data.get("name"),
            "about": request.data.get("about"),
            "image": request.data.get("image"),
            "category": request.data.get("category"),
            "brand": request.data.get("brand"),
            "store": request.data.get("store"),
        }

        articles_data = {
            "articles": request.data.get("articles")
        }
        if isinstance(articles_data["articles"], str):
            articles = articles_data["articles"].replace('\'', '"')
            articles = json.loads(articles)
        else:
            articles = articles_data["articles"]

        serializer = self.get_serializer(data=product_data)

        if serializer.is_valid():
            serializer.save()
            product = Product.objects.get(name=product_data["name"])
            for article_name in articles:
                Article.objects.create(
                    name = article_name,
                    product = product
                )
            response_data = {
                "message": "Məhsul əlavə edildi."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    lookup_field = "id"

class ArticleRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    lookup_field = "id"

class ApplicationCreateAPIView(CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

class SocialMediaListAPIView(ListAPIView):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

class AdvantageListAPIView(ListAPIView):
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer

class ActivityListAPIView(ListAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

class ServiceListAPIView(ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class MissionListAPIView(ListAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

class UserBasketItemListAPIView(ListAPIView):
    def get_queryset(self):
        return BasketItem.objects.filter(
            user = self.request.user
        )
    serializer_class = BasketItemSerializer
    permission_classes = (IsAuthenticated,)

class BasketItemCreateAPIView(CreateAPIView):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = serializer.validated_data['user']
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        # Try to get existing BasketItem
        basket_item, created = BasketItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            basket_item.quantity += quantity
            basket_item.save()

        self.instance = basket_item

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Return the updated BasketItem
        updated_serializer = self.get_serializer(self.instance)
        return Response(updated_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class BasketItemRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemCreateSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

class BasketCleanAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        serializer = BasketCleanSerializer(data=request.data)

        if serializer.is_valid():
            item_ids = serializer.validated_data['item_ids']
            count, _ = BasketItem.objects.filter(
                id__in = item_ids
            ).delete()

            response_data = {
                "message": f"{count} səbət elementi silindi."
            }

            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderCreateAPIView(CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        order_data = {
            "user": request.user.id,
            "amount": request.data.get("amount")
        }
        serializer = self.get_serializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            order_id = serializer.data["id"]
            order = get_object_or_404(Order, id=order_id)
            orderitems_data = {
                "products": request.data.get("products"),
                "quantities": request.data.get("quantities")
            }

            if isinstance(orderitems_data["products"], str):
                products = orderitems_data["products"].replace('\'', '"')
                products = json.loads(products)
            else:
                products = orderitems_data["products"]

            if isinstance(orderitems_data["quantities"], str):
                quantities = orderitems_data["quantities"].replace('\'', '"')
                quantities = json.loads(quantities)
            else:
                quantities = orderitems_data["quantities"]
            
            for i in range(len(products)):
                product = get_object_or_404(Product, id=products[i])
                OrderItem.objects.create(
                    order = order,
                    product = product,
                    quantity = quantities[i]
                )
            BasketItem.objects.filter(product_id__in=products).delete()
            response_data = {
                "message": f"'{order.user}' {len(products)} məhsul sifariş etdi."
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            