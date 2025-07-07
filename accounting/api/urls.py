from django.urls import path
from accounting.api import views

urlpatterns = [
    path('purchase-create/', views.PurchaseCreateAPIView.as_view()),
    path('purchase-list/', views.PurchaseListAPIView.as_view()),
    path('stock-list/', views.StockListAPIView.as_view()),
    path('addtostock/', views.AddToStockAPIView.as_view()),
    path('sale-list/', views.SaleListAPIView.as_view()),
    path('sale-create/', views.SaleCreateAPIView.as_view()),
    path('payment-list/', views.PaymentListAPIView.as_view()),
    path('payment-create/', views.PaymentCreateAPIView.as_view()),
    path('productaction-list/', views.ProductActionListAPIView.as_view()),
    path('customeraction-list/', views.CustomerActionListAPIView.as_view()),
]

"""
1. Stok elave et
2. Eyni anda bir nece satis
3. productionaction-retrieve
4. customeraction-retrieve

"""