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