from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem
)
from core.api.serializers import (
    CustomUserCreateSerializer, CustomUserRetrieveSerializer, SiteSettingsSerializer, BannerSerializer, ProductCategorySerializer,
    BrandSerializer, ProductSerializer, ApplicationSerializer, SocialMediaSerializer, AdvantageSerializer,
    ActivitySerializer, ServiceSerializer, MissionSerializer, BasketItemSerializer, BasketCleanSerializer
)

class UserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (IsAdminUser,)

class UserRetrieveAPIView(RetrieveAPIView):
    def get_object(self):
        return self.request.user
    serializer_class = CustomUserRetrieveSerializer

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
    serializer_class = BasketItemSerializer
    permission_classes = (IsAuthenticated,)

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