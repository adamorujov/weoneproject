from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Store, Product, ProductAbout, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem, WantedProduct
)
from django.utils.translation import gettext_lazy as _
from accounting.models import Sale, SaleList
from django.utils import timezone
from django.db import transaction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Əlavə məlumatlar", {"fields": ("address", "phone_number", "status")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

admin.site.register(SiteSettings)
admin.site.register(Banner)
admin.site.register(ProductCategory)
admin.site.register(Brand)
admin.site.register(Store)

class ArticleAdmin(admin.TabularInline):
    model = Article
    extra = 1

class ProductAboutAdmin(admin.TabularInline):
    model = ProductAbout
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ArticleAdmin, ProductAboutAdmin]

admin.site.register(Application)
admin.site.register(SocialMedia)
admin.site.register(Advantage)
admin.site.register(Activity)
admin.site.register(Service)
admin.site.register(Mission)
admin.site.register(BasketItem)

class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "add_to_sale")
    inlines = [OrderItemAdmin]

    def save_model(self, request, obj, form, change):
        old_value = False

        if change:  # update zamanı
            old_obj = type(obj).objects.get(pk=obj.pk)
            old_value = old_obj.add_to_sale

        super().save_model(request, obj, form, change)

        # yalnız False -> True keçəndə
        if obj.add_to_sale and not old_value:
            with transaction.atomic():
                salelist = SaleList.objects.create()

                sales = [
                    Sale(
                        seller=request.user,
                        customer=obj.user,
                        salelist=salelist,
                        product=item.product,
                        amount=item.quantity,
                        datetime=timezone.now(),
                        price = item.product.price
                    )
                    if obj.user.status == "S"
                    else
                    Sale(
                        seller=request.user,
                        customer=obj.user,
                        salelist=salelist,
                        product=item.product,
                        amount=item.quantity,
                        datetime=timezone.now(),
                        price = item.product.discount_price
                    )
                    for item in obj.order_orderitems.all()
                ]

                Sale.objects.bulk_create(sales)

@admin.register(WantedProduct)
class WantedProductAdmin(admin.ModelAdmin):
    list_display = ("user", "search", "created")