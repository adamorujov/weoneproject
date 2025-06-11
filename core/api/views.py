from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem
)
from core.api.serializers import (
    CustomUserCreateSerializer, SiteSettingsSerializer, BannerSerializer, ProductCategorySerializer,
    BrandSerializer, ProductSerializer, ApplicationSerializer, SocialMediaSerializer, AdvantageSerializer,
    ActivitySerializer, ServiceSerializer, MissionSerializer, BasketItemSerializer
)

class UserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserCreateSerializer
    permission_classes = (IsAdminUser,)

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

class BasketItemCreateAPIView(CreateAPIView):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemSerializer