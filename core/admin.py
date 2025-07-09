from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem, Article, Order, OrderItem
)
from django.utils.translation import gettext_lazy as _

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

class ArticleAdmin(admin.TabularInline):
    model = Article
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ArticleAdmin]

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
    inlines = [OrderItemAdmin]