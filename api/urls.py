from django.urls import path
from .views import auth as auth_views
from .views import product_views, invoice_views, admin_views, motoboy_view
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
	path('auth/me/', auth_views.GetMeView.as_view(), name='auth-me'),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),

	path('get-products/', product_views.ProductListView.as_view(), name='product-list-create'),
    path('admin/product/', product_views.create_product, name='product-create'),
	path('products/<int:pk>/', product_views.ProductDetailView.as_view(), name='product-detail'),
    
	path('admin/motoboys/', motoboy_view.MotoboyListCreateView.as_view(), name='motoboy-list-create'),
    path('admin/update-motoboy/<int:pk>', motoboy_view.MotoboyUpdate.as_view(), name='Update-Motoboy'),
    path('admin/delete-motoboy/<int:pk>/', motoboy_view.MotoboyDelete.as_view(), name='Delete-Motoboy'),    
	
	path('admin/stats/', admin_views.AdminStatsView.as_view(), name='admin-stats'),
	path('admin/users/', admin_views.AdminUserListView.as_view(), name='admin-user-list'),
	# orders / checkout
	path('checkout/', order_views.CheckoutView.as_view(), name='checkout'),
	path('orders/<int:pk>/', order_views.OrderDetailView.as_view(), name='order-detail'),
    path('admin/orders/', order_views.OrderList.as_view(), name='list-order'),
	path('my-orders/', order_views.MyOrdersView.as_view(), name='my-orders'),
]
