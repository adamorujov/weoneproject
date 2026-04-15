from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.pagination import PageNumberPagination
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Store, Product, ProductAbout, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem, WantedProduct
)
from core.api.serializers import (
    CustomUserCreateSerializer, CustomUserSerializer, CustomUserSerializer, SiteSettingsSerializer, BannerSerializer, ProductCategorySerializer, ProductCreateSerializer,
    ProductUpdateSerializer, ArticleSerializer, BrandSerializer, StoreSerializer, ProductSerializer, ApplicationSerializer, SocialMediaSerializer, AdvantageSerializer,
    ActivitySerializer, ServiceSerializer, MissionSerializer, BasketItemSerializer, BasketItemCreateSerializer, BasketCleanSerializer,
    OrderCreateSerializer, ProductListSerializer, CustomUserRetrieveSerializer, WantedProductCreateSerializer
)
from django.shortcuts import get_object_or_404
import json
from django.db.models import F, Subquery

class CustomPagination(PageNumberPagination):
    page_size = 10  # default olaraq hər səhifədə 10 obyekt
    page_size_query_param = 'page_size'  # istifadəçi ?page_size=20 yaza bilər
    max_page_size = 100  # maksimum icazə verilən ölçü

class CustomUserPagination(PageNumberPagination):
    page_size = 5  # default olaraq hər səhifədə 10 obyekt
    page_size_query_param = 'page_size'  # istifadəçi ?page_size=20 yaza bilər
    max_page_size = 100  # maksimum icazə verilən ölçü

class ShortProductCustomPagination(PageNumberPagination):
    page_size = 10  # default olaraq hər səhifədə 10 obyekt
    page_size_query_param = 'page_size'  # istifadəçi ?page_size=20 yaza bilər
    max_page_size = 100  # maksimum icazə verilən ölçü

class UserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (IsAdminUser,)

class UserListAPIView(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = CustomUserPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name", "phone_number", "address"]

class UserRetrieveAPIView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserRetrieveSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = "id"

class UserRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    def get_object(self):
        return self.request.user
    serializer_class = CustomUserSerializer

class ProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
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

from django.db.models import Case, When, IntegerField, Value

class ShortProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = ShortProductCustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "degree", "brand__name", "store__name", "category__name", "articles__name"]

    def get_queryset(self):
        # return Product.objects.select_related("brand").prefetch_related("articles").order_by("-updated_at")
        return Product.objects.select_related("brand").prefetch_related("articles").annotate(
                stock_status=Case(
                    When(amount__gt=20, then=Value(1)),   # stock_in
                    When(amount__gt=0, then=Value(2)),    # stock_out
                    When(amount=0, then=Value(3)),        # out of stock
                    output_field=IntegerField(),
                )
            ).order_by("stock_status", "-updated_at")

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "degree", "brand__name", "store__name", "category__name", "articles__name"]

class RecentProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = ShortProductCustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "degree", "brand__name", "store__name", "category__name", "articles__name"]

    def get_queryset(self):
        qs = (
            Product.objects
            .select_related("brand", "store", "category")
            .prefetch_related("articles").order_by("-updated_at_purchase_time")
            .filter(price__gt=0)
        )
        limited_ids = qs.values_list("id", flat=True)[:300]
        return qs.filter(id__in=Subquery(limited_ids))

class CategoryProductListAPIView(ListAPIView):
    def get_queryset(self):
        category_id = self.kwargs.get("id")
        return Product.objects.filter(
            category__id = category_id
        ).select_related("brand").prefetch_related("articles")
    serializer_class = ProductListSerializer
    pagination_class = CustomPagination

class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer

    def create(self, request, *args, **kwargs):
        product_data = {
            "name": request.data.get("name"),
            "degree": request.data.get("degree"),
            "image": request.data.get("image"),
            "category": request.data.get("category"),
            "brand": request.data.get("brand"),
            "store": request.data.get("store"),
        }

        articles_data = {
            "articles": request.data.get("articles")
        }
        abouts_data = {
            "titles": request.data.get("titles"),
            "contents": request.data.get("contents")
        }
        if isinstance(articles_data["articles"], str):
            articles = articles_data["articles"].replace('\'', '"')
            articles = json.loads(articles)
        else:
            articles = articles_data["articles"]

        if isinstance(abouts_data["titles"], str) and isinstance(abouts_data["contents"], str):
            titles = abouts_data["titles"].replace('\'', '"')
            titles = json.loads(titles)
            contents = abouts_data["contents"].replace('\'', '"')
            contents = json.loads(contents)
        else:
            titles = abouts_data["titles"]
            contents = abouts_data["contents"]

        serializer = self.get_serializer(data=product_data)

        if serializer.is_valid():
            product = serializer.save()
            response_data = {}
            if articles:
                for article_name in articles:
                    # if Article.objects.filter(name=article_name, product=product, product__store=product.store).exists():
                    #     response_data["errors"] = f"{article_name} artıq mövcuddur."
                    if Article.objects.filter(name=article_name).exclude(product__name=product.name).exists():
                        response_data["errors"] = f"Artikl '{article_name}' artıq mövcuddur."
                    else:
                        Article.objects.create(
                            name = article_name,
                            product = product
                        )
            if titles and contents:
                for i in range(len(titles)):
                    ProductAbout.objects.create(
                        product = product,
                        title = titles[i],
                        content = contents[i]
                    )
            response_data["message"] = "Məhsul əlavə edildi."
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ProductCreateAPIView(CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductCreateSerializer
    
class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "id"

class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    lookup_field = "id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()

        articles = data.pop("articles", None)
        articles = str(articles) if articles else articles
        article_ids = data.pop("article_ids", None)
        article_ids = str(article_ids) if article_ids else article_ids
        titles = data.pop("titles", None)
        titles = str(titles) if titles else titles
        contents = data.pop("contents", None)
        contents = str(contents) if contents else titles
        about_ids = data.pop("about_ids", None)
        about_ids = str(about_ids) if about_ids else about_ids

        if isinstance(articles, str):
            try:
                articles = articles.replace('"', '\\"')
                articles = articles.replace('\'', '"')
                articles = json.loads(articles)
                articles = json.loads(articles[0])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'articles'"}, status=400)
            
        if isinstance(titles, str):
            try:
                titles = titles.replace('"', '\\"')
                titles = titles.replace('\'', '"')
                titles = json.loads(titles)
                titles = json.loads(titles[0])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'titles'"}, status=400)
            
        if isinstance(contents, str):
            try:
                contents = contents.replace('"', '\\"')
                contents = contents.replace('\'', '"')
                contents = json.loads(contents)
                contents = json.loads(contents[0])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'contents'"}, status=400)
            
        if isinstance(article_ids, str):
            try:
                article_ids = article_ids.replace('\'', '"')
                article_ids = json.loads(article_ids)
                article_ids = json.loads(article_ids[0])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'article_ids'"}, status=400)
            
        if isinstance(about_ids, str):
            try:
                about_ids = about_ids.replace('\'', '"')
                about_ids = json.loads(about_ids)
                about_ids = json.loads(about_ids[0])
            except json.JSONDecodeError:
                return Response({"error": "Invalid JSON in 'about_ids'"}, status=400)

        serializer = self.get_serializer(instance, data=data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            if(hasattr(product, "stock")):
                product.stock.amount = product.amount
                product.stock.save()

            article_ids = article_ids if article_ids else []
            articles = articles if articles else []
            response_data = {}
            if articles:
                if article_ids:
                    for i in range(len(article_ids)):
                        product_article = Article.objects.get(id=article_ids[i])
                        product_article.name = articles[i]
                        if Article.objects.filter(name=product_article.name, product__name=product.name, product__store__name=product.store.name).exists():
                            response_data["errors"] = f"Artikl '{product_article.name}' artıq mövcuddur."
                        elif Article.objects.filter(name=product_article.name).exclude(product__name=product.name).exists():
                            response_data["errors"] = f"Artikl '{product_article.name}' artıq mövcuddur."
                        product_article.save()
                if len(articles) > len(article_ids):
                    # 0 1 2   0 1 2 3 4 5
                    for i in range(len(article_ids), len(articles)):
                        if Article.objects.filter(name=articles[i], product__name=product.name, product__store__name=product.store.name).exists():
                            response_data["errors"] = f"Artikl '{articles[i]}' artıq mövcuddur."
                        elif Article.objects.filter(name=articles[i]).exclude(product__name=product.name).exists():
                            response_data["errors"] = f"Artikl '{articles[i]}' artıq mövcuddur."
                        else:
                            Article.objects.create(
                                name = articles[i],
                                product = instance
                            )
            about_ids = about_ids if about_ids else []
            contents = contents if contents else []
            titles = titles if titles else []
            if titles and contents and len(titles) == len(contents):
                if about_ids:
                    for i in range(len(about_ids)):
                        product_about = ProductAbout.objects.get(id=about_ids[i])
                        product_about.title = titles[i]
                        product_about.content = contents[i]
                        product_about.save()
                if len(titles) > len(about_ids):
                    for i in range(len(about_ids), len(titles)):
                        ProductAbout.objects.create(
                            product = instance,
                            title = titles[i],
                            content = contents[i]
                        )
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

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
            

class WantedProductCreateAPIView(CreateAPIView):
    queryset = WantedProduct.objects.all()
    serializer_class = WantedProductCreateSerializer
    permission_classes = (IsAuthenticated,)