from django.urls import path
from core.api import views

urlpatterns = [
    path("user-create/", views.UserCreateAPIView.as_view()),
    path("user/", views.UserRetrieveAPIView.as_view()),
    path("settings/", views.SiteSettingsListAPIView.as_view()),
    path("banner-list/", views.BannerListAPIView.as_view()),
    path("settings/", views.SiteSettingsListAPIView.as_view()),
    path("category-list/", views.ProductCategoryListAPIView.as_view()),
    path("brand-list/", views.BrandListAPIView.as_view()),
    path("product-list/", views.ProductListAPIView.as_view()),
    path("category-product-list/<int:id>/", views.CategoryProductListAPIView.as_view()),
    path("application-create/", views.ApplicationCreateAPIView.as_view()),
    path("socialmedia-list/", views.SocialMediaListAPIView.as_view()),
    path("advantage-list/", views.AdvantageListAPIView.as_view()),
    path("activity-list/", views.ActivityListAPIView.as_view()),
    path("service-list/", views.ServiceListAPIView.as_view()),
    path("mission-list/", views.MissionListAPIView.as_view()),
    path("user-basketitem-list/", views.UserBasketItemListAPIView.as_view()),
    path("basketitem-create/", views.ProductListAPIView.as_view()),
    path("basketitem-clean/", views.BasketCleanAPIView.as_view()),
]