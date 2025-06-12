from django.contrib import admin

from core.models import (
    CustomUser, SiteSettings, Banner, ProductCategory,
    Brand, Product, Application, SocialMedia, Advantage,
    Activity, Service, Mission, BasketItem
)

admin.site.register(CustomUser)
admin.site.register(SiteSettings)
admin.site.register(Banner)
admin.site.register(ProductCategory)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Application)
admin.site.register(SocialMedia)
admin.site.register(Advantage)
admin.site.register(Activity)
admin.site.register(Service)
admin.site.register(Mission)
admin.site.register(BasketItem)