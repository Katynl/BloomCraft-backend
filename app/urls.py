from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),

    path('orders/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/my/', views.UserOrderListView.as_view(), name='user-orders'),
    path('orders/my/<int:pk>/', views.UserOrderDetailView.as_view(), name='user-order-detail'),

    path(
    "admin/orders/",
    views.AdminOrderListView.as_view(),
    name="admin-orders",
),

path(
    "admin/orders/<int:pk>/",
    views.AdminOrderDetailUpdateView.as_view(),
    name="admin-order-detail-update",
),

path(
    "admin/products/",
    views.AdminProductListView.as_view(),
    name="admin-products",
),

path(
    "admin/products/create/",
    views.AdminProductCreateView.as_view(),
    name="admin-product-create",
),

path(
    "admin/products/<int:pk>/",
    views.AdminProductUpdateView.as_view(),
    name="admin-product-update",
),

path(
    "admin/products/<int:pk>/delete/",
    views.AdminProductDeleteView.as_view(),
    name="admin-product-delete",
),

path(
    "admin/feedback/",
    views.AdminFeedbackListView.as_view(),
    name="admin-feedback",
),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path(
    'password-reset-simple/',
    views.SimplePasswordResetView.as_view(),
    name='password-reset-simple'
),

    path('feedback/', views.FeedbackCreateView.as_view(), name='feedback'),
    
]