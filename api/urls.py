from django.urls import path
from .views import auth as auth_views
from .views import product_views, invoice_views, admin_views
from .views import order_views
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)

urlpatterns = [
	path('auth/register/', auth_views.RegisterView.as_view(), name='auth-register'),
	path('auth/admin/register/', auth_views.AdminRegisterView.as_view(), name='auth-admin-register'),
	path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('auth/admin/login/', auth_views.AdminLoginView.as_view(), name='auth-admin-login'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

	path('products/', product_views.ProductListCreateView.as_view(), name='product-list-create'),
	path('products/<int:pk>/', product_views.ProductDetailView.as_view(), name='product-detail'),

	path('invoice/pdf/', invoice_views.InvoicePDFView.as_view(), name='invoice-pdf'),
	
	path('admin/stats/', admin_views.AdminStatsView.as_view(), name='admin-stats'),
	path('admin/users/', admin_views.AdminUserListView.as_view(), name='admin-user-list'),
	# orders / checkout
	path('checkout/', order_views.CheckoutView.as_view(), name='checkout'),
	path('orders/<int:pk>/', order_views.OrderDetailView.as_view(), name='order-detail'),
	path('my-orders/', order_views.MyOrdersView.as_view(), name='my-orders'),
]
