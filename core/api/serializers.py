from rest_framework import serializers
from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem
)
from accounting.models import ReturnBack
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

class CustomUserSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()
    total_paid_amount = serializers.SerializerMethodField()
    customer_debt_amount = serializers.SerializerMethodField()
    our_debt_amount = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        exclude = ("password", "groups", "user_permissions")

    def get_total_amount(self, obj):
        total_amount = sum([sale.price for sale in obj.customer_sales.all()])
        return total_amount
    
    def get_total_paid_amount(self, obj):
        total_paid_amount = sum([payment.amount for payment in obj.payments.all()])
        return total_paid_amount
    
    def get_customer_debt_amount(self, obj):
        return self.get_total_amount(obj) - self.get_total_paid_amount(obj)
    
    def get_our_debt_amount(self, obj):
        customer_returnbacks = ReturnBack.objects.filter(
            sale__customer = obj
        )
        total_our_debt_amount = sum([returnback.amount for returnback in customer_returnbacks])
        return total_our_debt_amount
    
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

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    brand = BrandSerializer()
    articles = ArticleSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "image", "category", "brand", "date")

class ProductUpdateSerializer(serializers.ModelSerializer):
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

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("amount",)
