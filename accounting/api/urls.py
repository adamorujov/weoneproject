from django.urls import path
from accounting.api import views

urlpatterns = [
    path('purchase-create/', views.PurchaseCreateAPIView.as_view()),
    path('purchase-list/', views.PurchaseListAPIView.as_view()),
    path('stock-list/', views.StockListAPIView.as_view()),
    path('addtostock/', views.AddToStockAPIView.as_view()),
    path('sale-list/', views.SaleListAPIView.as_view()),
    path('sale-create/', views.SaleCreateAPIView.as_view()),
    path('bulk-sale/', views.BulkSaleAPIView.as_view()),
    path('payment-list/', views.PaymentListAPIView.as_view()),
    path('payment-create/', views.PaymentCreateAPIView.as_view()),
    path('productaction-list/<int:id>/', views.ProductActionListAPIView.as_view()),
    path('customeraction-list/<int:id>/', views.CustomerActionListAPIView.as_view()),
    path('returnback-list/', views.ReturnBackListAPIView.as_view()),
    path('returnback-create/', views.ReturnBackCreateAPIView.as_view()),
    path('expense-list/', views.ExpenseListAPIView.as_view()),
    path('expense-create/', views.ExpenseCreateAPIView.as_view()),
    path('invoice-list/<int:id>/', views.InvoiceListAPIView.as_view())
]