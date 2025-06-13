from rest_framework import serializers
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem
)
from django.contrib.auth.password_validation import validate_password

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "address", "password", "phone_number", "status", "is_staff", "is_superuser")

    def validate(self, data):
        validate_password(data["password"])
        return data
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username = validated_data["username"],
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            address = validated_data["address"],
            password = validated_data["password"],
            phone_number = validated_data["phone_number"],
            status = validated_data["status"],
            is_staff = validated_data["is_staff"],
            is_superuser = validated_data["is_superuser"]
        )
        return user
    
class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "is_staff", "is_superuser")
    
class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = "__all__"

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"
    
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    brand = BrandSerializer()
    class Meta:
        model = Product
        fields = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"

class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = "__all__"

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = "__all__"

class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = BasketItem
        fields = "__all__"

class BasketItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = "__all__"

class BasketCleanSerializer(serializers.Serializer):
    item_ids = serializers.ListField(
        child = serializers.IntegerField(), allow_empty=False
    )