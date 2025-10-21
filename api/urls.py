from django.urls import path
from .views import auth as auth_views
from .views import product_views, invoice_views
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
)

urlpatterns = [
	path('auth/register/', auth_views.RegisterView.as_view(), name='auth-register'),
	path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

	path('products/', product_views.ProductListCreateView.as_view(), name='product-list-create'),
	path('products/<int:pk>/', product_views.ProductDetailView.as_view(), name='product-detail'),

	path('invoice/pdf/', invoice_views.InvoicePDFView.as_view(), name='invoice-pdf'),
]
