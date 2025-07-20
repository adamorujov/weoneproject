from django.contrib import admin
from accounting.models import SaleList, CustomerAction, ProductAction

admin.site.register(SaleList)
admin.site.register(CustomerAction)
admin.site.register(ProductAction)