from django.urls import path
from accounting.api import views

urlpatterns = [
    path('purchase-create/', views.PurchaseCreateAPIView.as_view()),
    path('purchase-list/', views.PurchaseListAPIView.as_view()),
    path('stock-list/', views.StockListAPIView.as_view()),
    path('addtostock/', views.AddToStockAPIView.as_view())
]