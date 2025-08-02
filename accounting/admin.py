from django.contrib import admin
from accounting.models import SaleList, PurchaseList, CustomerAction, ProductAction, Stock

admin.site.register(SaleList)
admin.site.register(PurchaseList)
admin.site.register(CustomerAction)
admin.site.register(ProductAction)
admin.site.register(Stock)